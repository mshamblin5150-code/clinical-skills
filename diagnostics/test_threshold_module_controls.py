"""Portable synthetic tests; never import the application under observation."""
import contextlib
import base64
import hashlib
import json
import os
import py_compile
import io
import sys
import subprocess
import tempfile
import types
import unittest
import zlib
from pathlib import Path

import threshold_module_controls as child

# Source-only AST inventory from frozen baseline 08db6360. Bodies are never
# copied or imported. This compact fixture drives entirely synthetic modules.
FULL_IDS = json.loads(zlib.decompress(base64.b85decode(
    "c$~FeS&!pJlKwA#UJSg(zU*UlwLNaE*Y2t6fq`8th!mNUa*AZqnPjQtU%zqXp@S4D(Jzgbii$7KxFh(#-}Tz}MZb62?`>Tbey?@^"
    "x2I>@bhYkv^;)X-S+$?^i*76JboIOG_jc%ChPE~B?&<HU*MB1#s@R&gg71pjw7M9)_J!}^H?DAcr(9KQ?+d#vx>}XG(QW_TzpaN}"
    "8MSMz?@d{}!7z$Sm!_f-IIWsO!B>9_M)!pu+`D;K^_t*XmHT1`A7Q5b;96gp-WOYE|I{sf<%b$@j-6f|lUBM^&Kb>^G<QYwcjg`E"
    "KXe^{d9yLK>5prUU~65YdYE5lU0>L?KEnT1<$<^^JdlAA6~-4k7)ZM&Fwfeyu(w0mTjy!UGLEfNjV_dfCu-%ru8Pf(mSxou*r5XY"
    "rqGRnwY4oDcbquxbH&rgar!l3@$Bkjp~_Nsu-TTDVGloPVWHb@z|APF8=vY6?9aEo>YweqcK%n}?*ZTo{^#lMPE{}#dQR>$?j``h"
    "qj;+c&Gf3r>EgE14`}II8;${f;ra70zURw_p<U!IEk6zuhQIj^*7*SIRXBU_#X-U4TL~6;#Gnh<2M>&dwsr&8Y|9wMX6Wg=7EW8m"
    "!-#9L$^hsRHTDgl@nfmpHC(n1wgOp;buhvVTf-HD9ZIW(=W=u$uW(A*3P<xo=f!_jJN?Du7f=36??0OzFq5zl9sH5kxV6A%cX+GA"
    "-Nv2fCsqY>rte`wxCRGx%obnf58%M+>$(62RPM(w*(W|TPmKJ{{s>I-)ef$VGHZjJqEj%r4Ll21*b*9XGfz*hL7R4_KUg8j6mb2V"
    "-VVs496SZP*6(32cY{X0bwBRb)OcX=xG0Bw3GZm!EM^h-d1&Ph_txHz_NI?`>)mcZnVv5r4B*ivl)>VbI19tCtmb(T6&5$haNztq"
    "xRa(HRVr>`!6o|WY6C2e_l(9L@$`p52CR<w5g0KDUtH!j&|r=}TR*twz+QkifRwRsLq`+8|Ad2RYTsIWXv5iq{ld-15jcl@L>M?Q"
    "Q<xBp0On`AhwyM;)TY+g&RTxb;Z8Wv1vjdEdk7Eo0FR<4!Qq59b{LoXx9F03<qukSg{lo4F}3l!h2=xy#CJCuxUlBkqqDhHb^XXx"
    "@C+XrCkS#raEJY<-gb*-8Xf%3)~FGp92e>xY(zR0_hR7Xr0aoFxpN@fT7@gMN8VhZBE$;IwY_=-)1#t?r@22E-k5NvAEKJ=`N4ps"
    "M_Da%RAo<_&nqfiH7Gt~pwFT+eKXp9A4LP6&7iUdU7ap{rCZyWRz<zGH;9k2<IQxVd|(1ac9_AUa>n<b_-2QC@-oUT*c|Zfy9Opz"
    ";#hGda$O0xw*iJ$iM|M$?Z=%6q!Iw5XnpBSC*%l7@fn~8<VdqXT{amfdUxSl({(JE^@nac-s2Khaq0fTVgnxsk}%A+H(T68P*ln{"
    "FV|d#Ys+$Q4jIcL^1c4($(#oHA$KWT>?9<4k<wC@wyq7@D@)K?Ir(yq__U-Oh+~0!UCAv`LuKgfwrC#K=1-#c0G{k9ZnkWXut>14"
    "8!~!PxJ|Q@>oBG*#RiKE(RM@4iwJxRm$0lgJc)A_bw4g8?&bnKWV><Oc!C0Ywq0o7z*>?$vsIw>mP=Q#s}(5dX{fYAYhD@JXQk*U"
    "vytL}Z-IekXz5z5D^iof@Gp<3S+Z593*YKpwgY%qX)?aF-MmZs@23{tVQ)Q99h!|ME_Qyp!l~OTQ_otYbNXUAB?LNGIQT{5HN>`k"
    "q}Nqj6cEP)IsiuL*metAX8$tOQKv5DyJ7>p`;GNnlxiY?Xw)!m!1r7BE3HGFY%074ye`x0d4+OsD|=2p-kr+$at}(hNS|R`HNPZX"
    "neCRHDCz!tav`x^95Clo#97w1-NAnIWKp%xxC$@sk;HmMniH}ExbgEL=o<eqD4^RPNls<Vi_S=zmTW2C%kwRo4~Z*V<ISVrdFG0w"
    "qQD;vx#JqvUBwG%9O{F9!B#}6!pr7+VjfY!o4X&tmw+eazUdQHD0oca7Lk(>z9(e<z<dRuLG>n|@e-U%#mH$O;`D|5K&<;H!$G-r"
    "@RLx<7;Pz(mLQ#x2osUB3$o(Tsfgf-B37A3lt!=JJ8XEOJ>|K*N*dM%xA%y~2>Fj3+(X$}bekbdKNm*P53>Y`eK?f{(&QgiMPot0"
    "2Kp%2jaNITweak_V1hD4^D<;&q2`jb${a7830i=ga{U_E(6UAef`;Vj`BDXC3>{jhdfGx5aY-Nu+6|E~NV8T{<f#7zqn_aA<A{v~"
    "3)g5Ay?$>xBva|yz(;rv<Pk2{wAc2MFb^->EHb9}7+hTPZEeS`(M!T0;<v;qY)c}9Jt^?DZfKw)K|vDsstz8B`Q(A!U2JDq+uVI0"
    "eKl+z!Z)M^&j%u28kPrSR4oP&8d5%)TPGZC!8wgW!iMMzEet#6$<>;3`}uS)Pvz;sNoPeI@WG0oG(807i~p+KRp%zTEm_|T%70}`"
    "7Nzrf#yI^<1w#jZMw%wX-sVExyjfQe(n_&AJ_;j$h0oqYpJE5Hkv{G>D`&S<=rOXq$uRvbtUDb<ar%?VB}{gP_j(inudXn!EJ%jm"
    "ra+k}+k1sRxy1<Q%1Vm6(i}2x@12JeNs%}!L4Wg^sTDnjcae;og;)VuTR8SwKHF{B>c!N_3KGWSx&cFh9%ewEo1{5P3~`M5XXfJ7"
    "FQzg5C%sqi#yU_^duQtyp+cVlvlk4!)oP<_1n^yL`rs7CXFx0P<A;70R5T5SR+VL#Op^UKB>WtV;I8M{zy<3OgP0Mq*`aBaJ4UOO"
    "<~4rjW*~0lTlC!WJtnbUbChonH>HLF;2$3VsRoR#U_wS(El=Jr)uH-oC3Y?%irM@Fc&rid;2oRkARTH$r$k)Eo%KeXaP-qza9`1U"
    "`f4%gDOmx}wnN=k=4nf?x>zaXa2Wb_@Nt-6sl|QS9ZB@t!y1r$#eig`dyUx_qOzbw<YhpYJOZN|WlBL=j7qGix1A}$429nSlI~!o"
    "LGU1LHv235+h*S336}r}c=I97RF;&SCNyvC85thOAA=rr#k{zNr67eGB^mk0;JMLQ%Qd<bib6FOE+MXMSXWwP{f;LbJ^-)a6E>6Q"
    "2=RCe1Fu=~V-{yHJm#?!ICtm>?%0yUgBeHrZuGnZD8y;?_$;e@ad~Gr&kPR%B?75-JVbhpI4drJyUAu#DEaCnI6_lR&f!Pi-Dmda"
    "A74n!hbSD2d=4tIV1}zwp%3Q3ryWGBYIn3?WLKi+V;G&%1ePB_MuS2Z&R=E4-w5P`bF95Z9`7;g#V?e*_LI?d^|SI%a7nA7MC2FB"
    "GRc|W79Ro@h@7vsto8K3n>GV-;r1M(pvZG!8ZtXZd2conO04^>)xTo&^>weh6Km`w`%Z<AoOze@UsOu*Por=j7?8#Zej&NhA9IU8"
    "In;D~POOfwizJaJG>mBgQg2cDM29`a7<VZ!h~wtt*{IfR`CO?96=NEUcOi^hi3Q7MA-QG=N^<-_tJjUX3kdElCtmI;F$@_YDy}G!"
    "t9%{hF5ZQKN{o7kK~vH}TpkLZv%CuG80=wnD?M!rif=Hd;U%RzB9hRJHyWPB-Q4K@pmlpA%sPcCfTDd#>@Dseo$7RC!eH(JqQxSn"
    "(u?NQAK3;~q7*(#JwIj?x<OvWq=_frOPBls*>N&Ae7E@PpWt$R@t?&Y*42}Ldc|PYH~2x+_9^}+b|@>#Wa-k`GGfA{JiSNZa-b_&"
    "NRq_CsQt0CS@sTQJWqvoXAS}H67p}lO8IaI6SMKaN~36{BGEYQJevoaxKIvAS%0=V#<iYtcL@&!><e2)|AdoLf7{2*T24KDX2(G;"
    "K00SNk~6o*>vZA~lO-l66EQ{OZtV1;5t!ut9Pnw}19&PX0eMh6{6I!>3((D^Gi5nE&Pc>1YNp8p+3(S;MXF<9zrZ=ce46tV&v2Um"
    "g&eoW#JRKV!+QyeM=OLtDJK+Du_zY!*I>|5WQOt=P?yM@<m9aY&=#1tatwse7hgR<7p&G}R8f>Dd@&s^&+Dt4?IwcpzYcXxna-@Y"
    "`X{HKKr}jvyS@;eZ$RcpoXA%anpd3_6cI4&ZljWilROI2<7r58xCv_QA+e4$P`ZX>!m^$wsa<S$|0S>_@d%p{(HKU{#k7i|6Xa_r"
    "Z@2`8bv1pPX)v&`pU`jdY#p#f%aS@Oz(j=o8a;4u3@?VqB(o5A=5Byi(yl~+=lNt=THFKV(cHjVm|Dv$a7Gg9RifpR_B)KHRNR7*"
    ";ME?pMot&Ycn+U)vQ#tllbrk(4z5Z!0R1v4q>?E`alEuM6=-elZQRJZh4iO(n7)Eq4?N|?$cxU&Y-_0GWef&vw^xkkqZaV2+NahZ"
    ";CLVG3tW&hF2mQR5T_?Qmsszbtnj#vfC(1}fzf}^V^TH>x<JUxQuHG(8=_R%aktq#II_b1J_LywE?DJo%?Au*0T9nT7z?nw%^2=i"
    "P@1D>ELd*nxuPv1yFe2EgJP8^OmU+#x<oG5*U?K_p<z#@H;t;%I%GdXkTH`X+FSHVC@Q!%<T0bnk@e_yn3DMz;m&lNe33Jz_#2PP"
    "YhYb0Z{y$Q0z^ig9_&dGC(X3BoCjIjdT1hy)0shyHa1LuCSGPkvKfn9f=Zi2Zk<IvwLyurn7EZ%DWQK#GuIm?!_4R8C6$MwV9An9"
    "ju=izM28wbiQ%kyv`<PHLhNzRbyb1KV!9J)hTDQ1K1Fc8&bwX2Qn_U9st3k_ATllMH^4;3X#N9D+*c{_)SeW5R3x6->Q|IQPd{<M"
    "EBRtrJIqqWf+?x1D<S(8aX-p>s6ve-`S4Q$h2DWIaS}BcHvfWqRMfiKtvP^{h7cVaQDFozhJ)jDPbwH*6PK%w!%sM;ji#!0JFJXG"
    ")rtH{D=)ja-Aq{ZSg4!a8dK`vJzy-OrAROMg(pL<52Mg|3MCR7)wbiy_ku3)lcd1Lz*Wa$!eP5LABl0pA7&G&hTzU>CI5^wieqjj"
    "Rg7TJPhmO9rb{q1=?PWy0xRSYw;`8j*P1^my2P%i5F^f+D!Cm;CC~*#rwo-s9DQ$5w<OETDEY)0FT}dVEzLt3<$9O&HLz1y3%K_i"
    "Eh*`}Y0z!jR!Nb#V{yU{_->sNZ8KGmMi0WeQ=9`f6QJZ$Q#Se7L_pUKRX&l1I+M;Gp0}75k4zC3!@yaALjk|(Kzis{-TlM&Mbi}f"
    "9Y()6-(&8Xtlw>KX_^MTNUW}7vK6dEJe9uFB`}*ZEgL1PEl2YWvN?>k_*foZk)|@_w;<v*J4W)$p?Xuk!TtY_AO15&(ST!Cpcoy3"
    "!vir{^Wc^b=je2R=bqMsHoJWfT*b3WW}A(zkJw`(O;GXW1GUvzU`ga_pitYK*&V)M)&6fCW+PgcA7&t0QvOW}U3jw-CNm>}eu_4*"
    ")eY=Z6H6N!b!7Je=jbpp!QmH@!LBG-aycG3V&vPr<T<3uXpHPS(=@0>VYMLExsTTzOanP}V1G~S#{jw&Gp$NBR3|bn@otc2=5#iE"
    ">P11hKYbj(Q)pj|!(ct{3ulFY1xB5R`Pr%FG^#*8dGj!^Ge+)}ycQ=CDH?>fO)2kf$_&mdlPUZ5l5%EYvaxpIkxO2bX}Nz%TLv1k"
    "&6~kfj6rIZVq=pm{mJVcn%<*#;3fu9CLrn~z%CX1jxDSObdSgxKnPF`2_=UuxvUoiTk;XfE@sL)`iUQ)6xrc}bh1kFMO4H!R$IPN"
    "60V~f2~<0Le!n=MZ@e+VIqf#MfwM!OSyX{AUo&zH`x6^-JTiNZbYgj)ou1ubFuk0*^7N{<6XzdzB0Al^p_O^+V5M6o#<J5r#beZ@"
    "XZ1R@W~h4;TTb8wWoH77nY2<ecqY?1uTxG}o&y=|7!dWhrQGN$b3D#SV;;q+a~!dmg_&)%EKikL(bKNZ5f~~OVFqc?I160hojidQ"
    "_}d(>?awlt^PG!pPwrfy6PI>=Zpg8HH_<%bR7ypIYgw9ckbk1$ttCtB4h)HASE;g?7JbN)(<g(=*9dcW12~;WG_^yRsI|jx&$T7&"
    "!p5Dg)o7QC>y)X%6=eXSLkJZjRscB-2OTKH5@HNv5p^C=mt0BjTE;5A;znVP0UZ|3PxG(`z|PAhFu`LPL|i(3;y<HIbsmf4dvi+g"
    "GzjPJd;@O&h9>+!NhkQlq`Zc`!l0*99oH1`r9DfaCaZqddA$jDg23@fs%r^}4C|oe;}6x<QuWDkSFGEKP9_o(4<Sn3k>uwDM}Mlu"
    "KgnsFN^_fqMlBo8hA+Nzwe6+aUzW6H8yNE<Zl?XF0CTQEMbnYFi>hL_2XSF;ArlyKYF%+_Bd=mPaoh@<PuWzdfDWYqXZCSoHFG~{"
    "J+>T88ggY-3Jl1mIfWEr1=CXMQcNZ0NvOlwZkMhK>#4DJ@}y$@v^tEbXS*=zx1U1WlCI2-v&30b5co!c!%WgFX5*p<<{+_>M?i>Z"
    "ma@d4oN#JmEvgB{@5}cWGl76x<AyMz+;{0cBhEUmM&pCFgnYDjnEz7&4hL%Ru3zLmh0?L*5Qc)Ek|GW_0f#CX+?&{)jE>R`iI0B6"
    ">Rb5sXKUZ0a}Krb0{&?=7hr@q{Dh19Hn}#WD`V317EcR#7wi;&8zYLQl8*F*rC_j)(^NeDPW~*yaF{qQV=&yhj)|3Eijb#~e&eSy"
    "=YU?VKMkg?eyWwY+qdvPDYC#qKCTVoMw3)~kUE&**=L`qznKGl4Jk`$MxBZ=IoXy+&R$VXMb*?oid%;*!Qf@y;?^d-IO^E$!DB=o"
    "(>xVsi6DuoJ-9&0LWlV&lDseSvfZ;lsd3h6k}C}`iz$iQB?y9pS+wC7t<;3wF!w?ejE)2X@fNXQ7=r+<;uEImJ+*L9^=A+p$Q&?j"
    "LifLILywb_8mcIfx!<Ft?fYC-qxcE=O-foI-5S9!T9K0T3wwS-bP2xUtc}F17&q$>!F)HmPB0TCbcBgja#Kv^-XZYRMdzc+q*%I3"
    "<zy309qxssV-$jg+<y-1EZDQ*B>t_&?*kBi20j79`^B_cQc!;fY4`>6W8ijS1GeZ(B(*%{tz)ybH3*|S8B8Va)0kxQ3Z!|FbYrCV"
    "ZtB0f8gb6GFZaYhq|0mcxvqvnA>h;{G=|(*_DFQ^hO&DfXh<I=@YR9Hx{U`4eeoMjq4(OPD(^i=O7!OF_T4z!PAN2ZLsORtE*XnV"
    "qN}#ji7^Y#QsTt~{AUB^CH(OpgT?s5SL=I_RzH~?%B&{`WBSZEX%v<G1Xz~s@etXb95gtnMk@^U<psWyr+Djtg@L@{7o3U;-~RXk"
    "hG47e=i0n#)uchh#%iQ4`E;t}kD^P&vEGEY2dYYVswxaue(~HdIq;J0fXgE8xk{eJxSjDc%>CQ+8!F}Dz(HLoerOHKC;q#?YWU=9"
    "qte*bX>)Dr2<@P=O%VU_!}PCIi}<RJaJ5Xi|1Y>xziofD{n-`>=b(<J#6GAj#9O?}$ca}$5wVx`6V6&2X8m|G=K$tt`QrPv;Qe^_"
    "VOY{1qE)sE;I(GG*XPUXB+vDS31}kk{+n|p;PX#ZK=`E(<v&>hyOgWvdQQloWUJBn84Aa8z)Z`LSf%*PPf)pO*UG@ShCJWQ5gR>U"
    "W+IOU0MNuEP-em&)j8V}Z+29Pe|#Yv#uZG`-0?c@S{qzvLD1i9SicxF%GZ*`W_C@)l1RaitF4G8Mgp*3u}TZ^O{rg{W}6boF0;eZ"
    "Dob#IE)-Y|HD4c445;R73UP_h4XQb12l11j0$|75jgGbPZSMO+oqlS&7og{D3)!K6p#ExTBdvu%&%_IwFY;l3j437SppoWMtv(4V"
    "DL{{o*l%n@u0#832#b^*b^=Vn$a@ihV;_Ix%yLPCykgOCvv~UQeu{Kr^;ThZeCiN>R&hf;f8dM9U_^$nK*bK}zQ7*oK^Ygnd*CIH"
    "Vdbs6$+O<(N<M|PoEc97|8`m?`J*qv_Wc?8`$b|+aJIimk<T%upw8$ReG}*;*&?g15WIWo_9+LSQUE{@I$1fn5ftcw--FD+P@Qu8"
    "rjNS;aZ#u$jM#;k0H^CXNgJI@pKNtRH72xv`fN}FybQ4_O$rHe$7y^`h`)WwXQEu{pHVww^Gb12|1Ews3-0uyPa)l?$%ug1HN#Uk"
    "4epu+dI~{ODR9h(zSb|EHjzufq;ov_tXUJpuh)SlI|Loo!EGsx_tV0wp|@E3T;5g{7T^j4id{V0_>Pu~MdzIPShX-!>b7tU0~ku)"
    "ZwK=DXR1rCfT#XS(+NAvpo6<Nyj&?;`21xJD?-BVO4}yP^mH|zt_+B*7S7aA1=d2jq^wSc8J7-%mBly|mKwq9onB%Q&Lw8^j@RKV"
    "0&mmHUib|xWY?X(7llVh0jF-Fx$Z*Tu{WiJ*FjLZ(Uf&J8;nW=Li+-0q{JH0_iPKK(v7o%<u$NR8UlINaTKNQhmasAF-lXFJ=Tm&"
    "D^oLpvp1`->-OS}Pstogm)x$!zx&WHgYplvo*{~2-D<Uylpmu;SI6+KM|>L}c^5ex#oejnYZ(u;)l+U>PD^16<J<$s$t@gN=hqJK"
    "n{iZ6ogU*vC-YGs!+4y2O#dS>!|6I=P(465B#B=kcv@YFH;g1{ypneT_LTS2*osR|r7%(yugOf>n`95fFO<_EM`tT;ntW!#14cgp"
    ">bK)><ho!#MfA?V*WV8ISAD=-g-c%zRga!}5Mm#6?B6(1HGCgn_67!Vo=h&|asY9A<=xu)v-Fi1<Gbnnx*wk~duQlXO7RsxN#IVl"
    "%)S>nc5KQ_AR|{B^)D<B;vVavk@rd?$XEBE>Ng-qsi@p?0`8+7sCyze2xX~gxv}ADL%{4O*jdc><GT|&Ik1eR=8v&C(-dfE+Vo8C"
    "qP*gOqt~LcO2w`ZdS|7S`JFGvjfQWt0COeo1d(cU`q0^k%R(m?bS6|*$J?ip+MFZt5T>Aro4nY=Gv^q5>HXJu{G%mStM*MIDK|yK"
    "e1hCBL~8VKWmcp;xOz=;_=eP3g7G#<VFjUbDdcvb6@dM7CW!xz1_<(tPjrI5_@5QNHx6&!SCzF)lXnJ5>uFJMm7F`)C}NM%$+mQJ"
    "F{7?`?&tRRIJzSwvW}-6)+wWl|2f2IiQSw8cO`zy3o4x*u?WC{iS~ZOu>%$#Fsh&78{DiHECLwtM1D@yI^if#yBs_LlmICmQ&sJ4"
    "DoBX_fvnhPHE1-95|TujUHlo{p}z#I-)HYs+?ta62E+e8Xb2c0TmzR9J?Z7nbw%&+N*yRvCGYT>uH##TcDYmHN22~W_zGh({O7&#"
    "@E&B1Ep~M#FlxP1W#+w|?x?y1GCL*V<xj!8&g$&>tDq=!Hr^^`33l*HpB~@j!A$3O%{wF9FTC}J92~+5W2Jw%%XHx7LO+h&hdk!f"
    "(qHP3#-)Y23VHbWT7XbmNA8I!`2W$)1`qc$IrSYGFzH-<V38Y@OA{;1wD_2r&(Q$K+x`GtV!IhE&n5Po6Z>Hf;0e=@Wf<HSM8W~n"
    "*4$MBCvAkmSV}#UW8&_OeEaKULwq$@&x5BpC-?2V=+=3=D&Z;$YK>U88?%E?TNUNKjBW*!=Fx8`tQTZzbiqw{8n4n#*~}rWYiPOQ"
    "ca;^{-VFCo(+*xd^!^X6tUp(L1G`CuBmCl*DK>f)=e&?*{tH;Il8Z6kFf2t@XJCue7-~PS8tgiK_6daJ7*~nAxUF>{<B;Vo52V|X"
    "{zEU0_1supRKcus3S5dsIKiJsZ}dBDM%!ODZLTz?_AOeka}_zAo3uRB4$A9P`3+?G`0yuQ?m#}RWpqz}JJO_UR*~uz`q;-8lZDXT"
    "5$=89Cw%m|uHsITXP)2oq++1O)3HMn_D<@7hh;7sey=2}tWptj2YY14RBvnTl)OYT#vqZW;Hj>4GaX>PLf7<v!HS^5x<My~*^oYS"
    "@;XMWbyd=uCI~Jb|01auJPs75ICDI(oX&XjeQR?rc|0k>tb||Opm5$p^nM{u{?-C194A3~Xtm4QnB%);7E^Yh)>9g)7f#7eWM1;A"
    "E)pXYr4|xf(-_$~ilH3v8+l2HNSN>b@Baa4;caC"
)))


def complete_source():
    source = "import unittest\n"
    current = None
    for identity in FULL_IDS:
        _, name, method = identity.split(".")
        if name != current:
            source += "class " + name + "(unittest.TestCase):\n"
            current = name
        source += "    def " + method + "(self): pass\n"
    return source


def encoded(row):
    return ("LAZY_PROOF_RESULT:" + json.dumps(row, sort_keys=True, allow_nan=False,
            separators=(",", ":")) + "\n").encode("ascii")


def receipt(action="discover"):
    with installed(complete_source()) as module:
        discovery = child.discover_module(module)
        detail = discovery if action == "discover" else {"discovery": discovery,
            **child.run_controls(module)}
    return {"schema": "threshold-module-child-v1", "action": action,
            "status": "passed", "module": "test_threshold_sheet",
            "module_origin_verified": True, "module_source_sha256": "a" * 64,
            **detail}


@contextlib.contextmanager
def installed(source):
    module = types.ModuleType("test_threshold_sheet")
    module.__file__ = "/synthetic/tools/test_threshold_sheet.py"
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    prior = sys.modules.get(module.__name__)
    sys.modules[module.__name__] = module
    try:
        yield module
    finally:
        if prior is None:
            sys.modules.pop(module.__name__, None)
        else:
            sys.modules[module.__name__] = prior


SYNTHETIC_CONTROLS = {
    "CoverageIsPerSource": (
        "test_a_second_sources_omissions_are_checked",
        "test_known_is_filtered_to_the_rows_citing_that_source",
        "test_the_ungraded_count_is_a_real_count_of_sources",
        "test_one_source_graded_and_one_not_reports_both_halves",
        "test_a_scope_out_still_discharges_its_recommendation",
        "test_the_mode_cross_check_is_per_source",
        "test_a_record_built_from_another_document_is_refused",
        "test_where_the_corpus_was_mounted_is_not_a_finding",
        "test_a_record_that_names_no_document_is_not_guessed_at",
        "test_the_class_check_reads_the_rows_own_source_record",
    ),
    "BindingARecordToEachSource": (
        "test_the_sweep_alias_wins_over_the_exact_name_root_and_is_reported",
        "test_each_sweep_alias_absence_is_named_before_recs_root_fallback",
        "test_an_explicit_recs_argument_beats_both_lookup_roots",
        "test_a_keyed_argument_binds_to_that_source",
        "test_an_untrusted_record_is_not_bound",
        "test_the_existing_provenance_hatch_can_accept_an_untrusted_record",
        "test_a_bare_path_binds_to_the_only_source",
        "test_a_bare_path_on_a_two_source_sheet_is_refused_rather_than_guessed",
        "test_an_unknown_source_key_is_an_error_and_not_a_silent_no_op",
        "test_the_same_key_twice_is_an_error",
        "test_recs_root_resolves_one_record_per_source_key",
        "test_an_explicit_path_that_does_not_exist_says_no_such_file",
        "test_a_record_the_root_does_not_hold_reads_as_never_built",
        "test_a_file_that_parses_and_is_not_a_record_is_ungraded_too",
        "test_every_absent_record_says_why",
        "test_an_unreadable_record_is_ungraded_rather_than_a_traceback",
    ),
    "WatermarkGate": (
        "test_conformance_foreign_provenance_needs_the_explicit_override",
        "test_conformance_command_override_is_explicit",
        "test_conformance_does_not_read_an_extraction_in_progress",
    ),
}


def control_source(body="self.assertEqual(2 + 2, 4)"):
    source = "import unittest\nevents = []\n"
    for name, methods in SYNTHETIC_CONTROLS.items():
        source += "class " + name + "(unittest.TestCase):\n"
        source += "    @classmethod\n    def setUpClass(cls): events.append('class-start:' + cls.__name__)\n"
        source += "    @classmethod\n    def tearDownClass(cls): events.append('class-end:' + cls.__name__)\n"
        source += "    def setUp(self):\n        events.append('setup')\n        self.addCleanup(events.append, 'cleanup')\n"
        source += "    def tearDown(self): events.append('teardown')\n"
        for method in methods:
            source += "    def " + method + "(self):\n        " + body + "\n"
    source += "class NotSelected(unittest.TestCase):\n    def test_never_run(self): raise AssertionError('wrong population')\n"
    return source


class ModuleDiscovery(unittest.TestCase):
    def test_fresh_id_reload_rejects_a_rebound_class_without_running_bodies(self):
        source = '''
import unittest
class Original(unittest.TestCase):
    def test_local(self): raise AssertionError("must not run")
class Replacement(unittest.TestCase):
    def test_local(self): raise AssertionError("must not run")
def load_tests(loader, tests, pattern):
    test = Original("test_local")
    globals()["Original"] = Replacement
    return unittest.TestSuite([test])
'''
        with installed(source) as module:
            with self.assertRaisesRegex(child.Refused, "^module_id_reload_mismatch$"):
                child.discover_module(module)

    def test_a_forged_id_cannot_hide_an_imported_testcase_class(self):
        source = '''
import unittest
class Concrete(unittest.TestCase):
    def test_local(self): raise AssertionError("must not run")
    def id(self): return "test_threshold_sheet.Concrete.test_local"
Concrete.__module__ = "unrelated_module"
'''
        with installed(source) as module:
            with self.assertRaisesRegex(child.Refused, "^module_discovery_failed$"):
                child.discover_module(module)

    def test_discovers_inherited_ids_and_reloads_without_running_bodies(self):
        with installed('''
import unittest
class Base:
    def test_inherited(self):
        raise AssertionError("discovery executed a body")
class Concrete(Base, unittest.TestCase):
    def test_local(self):
        raise AssertionError("discovery executed a body")
''') as module:
            row = child.discover_module(module)
        self.assertEqual(row["test_ids"], [
            "test_threshold_sheet.Concrete.test_inherited",
            "test_threshold_sheet.Concrete.test_local",
        ])
        self.assertEqual((row["test_count"], row["loader_errors"],
                          row["executed_test_count"], row["reload_verified"]),
                         (2, 0, 0, True))

    def test_discovery_refuses_duplicate_empty_and_loader_error_populations(self):
        sources = {
            "duplicate_module_ids": '''
import unittest
class Concrete(unittest.TestCase):
    def test_one(self): pass
Alias = Concrete
''',
            "module_discovery_failed": '''
def load_tests(loader, suite, pattern):
    raise RuntimeError("private synthetic marker")
''',
        }
        for reason, source in sources.items():
            with self.subTest(reason=reason), installed(source) as module:
                with self.assertRaisesRegex(child.Refused, "^" + reason + "$"):
                    child.discover_module(module)
        with installed("import unittest") as module:
            with self.assertRaisesRegex(child.Refused, "^module_discovery_failed$"):
                child.discover_module(module)


class ChildCommand(unittest.TestCase):
    def test_changed_source_and_import_exception_emit_only_finite_refusals(self):
        examples = (
            ("from pathlib import Path\np = Path(__file__)\np.write_bytes(p.read_bytes() + b'# changed')\n",
             "module_source_changed"),
            ('raise RuntimeError("private exception marker")\n', "child_unavailable"),
            ("import unittest\nclass Small(unittest.TestCase):\n    def test_small(self): pass\n",
             "module_population_changed"),
        )
        for source, reason in examples:
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as directory:
                repo = Path(directory).resolve()
                (repo / "tools").mkdir()
                raw = source.encode("ascii")
                (repo / "tools/test_threshold_sheet.py").write_bytes(raw)
                result = subprocess.run([sys.executable, "-B", str(Path(child.__file__).resolve()),
                    "--action", "discover", "--repo", str(repo), "--expected-source-sha256",
                    hashlib.sha256(raw).hexdigest()], capture_output=True, check=False, timeout=30)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, encoded({"schema": "threshold-module-child-v1",
                    "action": "discover", "status": "refused", "reason": reason}))
                self.assertNotIn(b"private exception marker", result.stdout)

    def test_receipt_is_canonical_bytes_even_when_host_text_stream_translates_newlines(self):
        raw = io.BytesIO()
        wrapper = io.TextIOWrapper(raw, encoding="utf-8", newline="\r\n")
        with contextlib.redirect_stdout(wrapper), contextlib.redirect_stderr(io.StringIO()):
            code = child.main(["--action", "discover", "--repo", "not-an-absolute-path",
                               "--expected-source-sha256", "a" * 64])
        wrapper.flush()
        output = raw.getvalue()
        self.assertEqual(code, 2)
        self.assertNotIn(b"\r", output)
        self.assertEqual(output.count(b"\n"), 1)

    def test_source_binding_cannot_execute_a_matching_timestamp_stale_bytecode_file(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            (repo / "tools").mkdir()
            target = repo / "tools/test_threshold_sheet.py"
            source = complete_source().encode("ascii")
            stale = b'raise RuntimeError("stale bytecode must not execute")\n'
            target.write_bytes(stale + b" " * (len(source) - len(stale)))
            os.utime(target, (1700000000, 1700000000))
            py_compile.compile(str(target), doraise=True)
            target.write_bytes(source)
            os.utime(target, (1700000000, 1700000000))
            digest = hashlib.sha256(source).hexdigest()
            result = subprocess.run([sys.executable, "-B", str(Path(child.__file__).resolve()),
                "--action", "discover", "--repo", str(repo), "--expected-source-sha256", digest],
                capture_output=True, check=False, timeout=30)
        row = child.validate_discovery_receipt(result.stdout, result.returncode, digest)
        self.assertEqual(row["test_count"], 345)

    def test_complete_synthetic_module_is_qualified_by_both_command_actions(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            (repo / "tools").mkdir()
            source = complete_source().encode("ascii")
            (repo / "tools/test_threshold_sheet.py").write_bytes(source)
            digest = hashlib.sha256(source).hexdigest()
            for action, validate in (("discover", child.validate_discovery_receipt),
                                     ("controls", child.validate_controls_receipt)):
                with self.subTest(action=action):
                    result = subprocess.run([sys.executable, "-B", str(Path(child.__file__).resolve()),
                        "--action", action, "--repo", str(repo), "--expected-source-sha256", digest],
                        capture_output=True, check=False, timeout=30)
                    row = validate(result.stdout, result.returncode, digest)
                    self.assertEqual(row["action"], action)
                    self.assertEqual(row["module_source_sha256"], digest)

    def test_discovery_command_rejects_wrong_module_origin_without_public_leak(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            (repo / "tools").mkdir()
            (repo / "tools/test_threshold_sheet.py").write_text(
                'print("private synthetic marker")\n__file__ = "/elsewhere/evil.py"\n',
                encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(Path(child.__file__).resolve()),
                                     "--action", "discover", "--repo", str(repo),
                                     "--expected-source-sha256", hashlib.sha256(
                                         (repo / "tools/test_threshold_sheet.py").read_bytes()).hexdigest()],
                                    capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, 'LAZY_PROOF_RESULT:{"action":"discover","reason":"module_origin_mismatch","schema":"threshold-module-child-v1","status":"refused"}\n')
        self.assertIn("private synthetic marker", result.stderr)

    def test_wrong_source_hash_is_refused_before_the_synthetic_module_imports(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            (repo / "tools").mkdir()
            (repo / "tools/test_threshold_sheet.py").write_text(
                'raise RuntimeError("synthetic body must not import")\n', encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(Path(child.__file__).resolve()),
                                     "--action", "discover", "--repo", str(repo),
                                     "--expected-source-sha256", "0" * 64],
                                    capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, 'LAZY_PROOF_RESULT:{"action":"discover","reason":"module_source_changed","schema":"threshold-module-child-v1","status":"refused"}\n')
        self.assertEqual(result.stderr, "")


class OriginalControls(unittest.TestCase):
    def test_stock_failure_error_skip_and_expected_outcomes_are_not_claimed_as_passes(self):
        with installed(control_source()) as module, contextlib.redirect_stderr(io.StringIO()):
            name = "BindingARecordToEachSource"
            methods = SYNTHETIC_CONTROLS[name]
            cls = getattr(module, name)
            def fail(self): self.fail("private synthetic failure")
            def error(self): raise RuntimeError("private synthetic error")
            def skip(self): self.skipTest("private synthetic skip")
            def expected_fail(self): self.fail("private synthetic expected failure")
            def success(self): pass
            setattr(cls, methods[0], fail)
            setattr(cls, methods[1], error)
            setattr(cls, methods[2], skip)
            setattr(cls, methods[3], unittest.expectedFailure(expected_fail))
            setattr(cls, methods[4], unittest.expectedFailure(success))
            row = child.run_controls(module)
        self.assertEqual((row["tests_run"], row["passed_count"], row["successful"]), (29, 24, False))
        for label, method in zip(("failure", "error", "skipped", "expected_failure", "unexpected_success"), methods):
            self.assertEqual(row[label + "_count"], 1)
            self.assertEqual(row[label + "_ids"], ["test_threshold_sheet." + name + "." + method])
        self.assertNotIn("private synthetic", json.dumps(row))

    def test_subtest_and_class_setup_errors_refuse_rather_than_relabel_identities(self):
        for source in (
            control_source("\n        with self.subTest(secret='private-marker'): self.fail('private-marker')"),
            control_source() + "\nBindingARecordToEachSource.setUpClass = classmethod(lambda cls: 1 / 0)\n",
        ):
            with self.subTest(), installed(source) as module, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaisesRegex(child.Refused, "^controls_result_unread$"):
                    child.run_controls(module)

    def test_fixed_twenty_nine_controls_keep_stock_class_and_cleanup_lifecycle(self):
        with installed(control_source()) as module, contextlib.redirect_stderr(io.StringIO()):
            row = child.run_controls(module)
            events = module.events
        self.assertEqual((row["tests_run"], row["passed_count"], row["failure_count"],
                          row["error_count"], row["skipped_count"], row["successful"]),
                         (29, 29, 0, 0, 0, True))
        self.assertEqual(events.count("setup"), 29)
        self.assertEqual(events.count("teardown"), 29)
        self.assertEqual(events.count("cleanup"), 29)
        self.assertEqual([event for event in events if event.startswith("class-")], [
            "class-start:BindingARecordToEachSource", "class-end:BindingARecordToEachSource",
            "class-start:CoverageIsPerSource", "class-end:CoverageIsPerSource",
            "class-start:WatermarkGate", "class-end:WatermarkGate",
        ])
        self.assertEqual(row["per_test_execution_observed"], False)


class ReceiptAdmission(unittest.TestCase):
    def test_output_noise_duplicate_keys_nonfinite_numbers_and_wrong_exit_do_not_qualify(self):
        valid = encoded(receipt())
        bad_outputs = (
            b"private-marker\n" + valid, valid + b"\n", valid + valid,
            valid.replace(b'"action":"discover"', b'"action":"discover","action":"discover"'),
            valid.replace(b'"test_count":345', b'"test_count":NaN'),
            b"LAZY_PROOF_RESULT:[]\n", b"LAZY_PROOF_RESULT:\xff\n", b"x" * 131073,
        )
        for output in bad_outputs:
            with self.subTest(length=len(output)), self.assertRaisesRegex(child.Refused, "^child_receipt_invalid$"):
                child.validate_discovery_receipt(output, 0, "a" * 64)
        for code in (1, 2, -1, True, None):
            with self.subTest(code=code), self.assertRaisesRegex(child.Refused, "^child_receipt_invalid$"):
                child.validate_discovery_receipt(valid, code, "a" * 64)

    def test_changed_ids_loader_errors_or_unverified_origin_cannot_preserve_qualification(self):
        original = receipt()
        mutations = (
            {"module_source_sha256": "b" * 64}, {"module_origin_verified": 1},
            {"status": "failed"}, {"test_count": True}, {"test_count": 344},
            {"loader_errors": 1}, {"executed_test_count": 1}, {"reload_verified": False},
            {"test_ids": original["test_ids"][:-1]},
            {"test_ids": [original["test_ids"][0]] * 345},
            {"test_ids": list(reversed(original["test_ids"]))},
            {"sorted_ids_sha256": "0" * 64}, {"extra": "private-marker"},
        )
        for change in mutations:
            with self.subTest(fields=list(change)), self.assertRaisesRegex(child.Refused, "^child_receipt_invalid$"):
                child.validate_discovery_receipt(encoded({**original, **change}), 0, "a" * 64)

    def test_exact_stock_control_counts_qualify_only_all_twenty_nine_passes(self):
        with contextlib.redirect_stderr(io.StringIO()):
            original = receipt("controls")
        row = child.validate_controls_receipt(encoded(original), 0, "a" * 64)
        self.assertEqual(row, original)
        self.assertEqual(row["tests_run"], 29)
        for key, value in (("tests_run", 28), ("tests_run", True), ("skipped_count", 1),
                           ("per_test_execution_observed", True), ("passed_count", 28)):
            with self.subTest(key=key), self.assertRaisesRegex(child.Refused, "^child_receipt_invalid$"):
                child.validate_controls_receipt(encoded({**original, key: value}), 0, "a" * 64)

    def test_exact_source_bound_discovery_receipt_qualifies_without_body_execution(self):
        original = receipt()
        row = child.validate_discovery_receipt(encoded(original), 0, "a" * 64)
        self.assertEqual(row, original)
        self.assertEqual((row["test_count"], row["executed_test_count"], row["reload_verified"]),
                         (345, 0, True))


if __name__ == "__main__":
    unittest.main()
