"""Compact-only Win32 capability; policy and handle lifetime belong to its caller.

This adapter is not a deletion service. Only newly registered owned captures may
enter open_capture; the coordinator must authenticate their native identity and
exact bytes and retain verified compact evidence before requesting disposition.
No path deletion, access fallback, sharing relaxation, or implicit marking exists.
"""
from pathlib import Path
import math
import re
import time

import generated_output_contract as g


class WindowsCompactAPI(g.WindowsMetadataAPI):
    """The receipt's inherited open remains read-only with FILE_SHARE_READ only."""

    def __init__(self, kernel=None):
        super().__init__(kernel)
        c = self.c
        class Disposition(c.Structure):
            _fields_ = [('DeleteFile', c.c_ubyte)]
        self.disposition = Disposition
        g.need(c.sizeof(Disposition) == 1, 'compact_native_abi_unavailable')
        signatures = {
            'SetFilePointerEx': ((c.c_void_p, c.c_int64, c.POINTER(c.c_int64), c.c_uint32), c.c_int),
            'ReadFile': ((c.c_void_p, c.c_void_p, c.c_uint32, c.POINTER(c.c_uint32), c.c_void_p), c.c_int),
            'SetFileInformationByHandle': ((c.c_void_p, c.c_int, c.c_void_p, c.c_uint32), c.c_int),
        }
        for name, (args, result) in signatures.items():
            function = getattr(self.kernel, name)
            function.argtypes, function.restype = args, result

    def open_capture(self, path):
        g.need(isinstance(path, Path) and path.is_absolute()
               and '..' not in path.parts
               and path.name in ('stdout.bin', 'stderr.bin')
               and re.fullmatch(r'command-[0-9]{4,10}', path.parent.name),
               'compact_capture_path_invalid')
        handle = self.kernel.CreateFileW(str(path), 0x80010000, 1, None, 3,
                                         0x00200000 | 0x08000000, None)
        g.need(handle not in (None, self.c.c_void_p(-1).value), 'compact_capture_unread')
        return handle

    def read(self, handle, limit, deadline):
        """Bounded same-handle read; deadline checks cannot cancel blocked Win32 I/O."""
        g.need(type(limit) is int and 0 <= limit <= g.MAX_FILE_BYTES, 'compact_read_limit_invalid')
        g.need(type(deadline) in (int, float) and math.isfinite(deadline), 'compact_read_deadline_invalid')
        g.need(time.monotonic() < deadline, 'global_budget_exhausted')
        g.need(bool(self.kernel.SetFilePointerEx(handle, 0, None, 0)), 'compact_capture_seek_failed')
        raw = bytearray()
        while True:
            g.need(time.monotonic() < deadline, 'global_budget_exhausted')
            requested = min(65536, limit + 1 - len(raw))
            buffer = self.c.create_string_buffer(requested)
            count = self.c.c_uint32()
            g.need(bool(self.kernel.ReadFile(handle, buffer, requested, self.c.byref(count), None)),
                   'compact_capture_read_failed')
            g.need(time.monotonic() < deadline, 'global_budget_exhausted')
            g.need(count.value <= requested, 'compact_capture_read_invalid')
            raw.extend(buffer.raw[:count.value])
            g.need(len(raw) <= limit, 'generated_file_oversize')
            if count.value == 0:
                return bytes(raw)

    def mark_delete(self, handle):
        """One disposition request; caller records uncertainty and owns one close."""
        disposition = self.disposition(1)
        g.need(bool(self.kernel.SetFileInformationByHandle(
            handle, 4, self.c.byref(disposition), self.c.sizeof(disposition))),
            'compact_capture_disposition_failed')
