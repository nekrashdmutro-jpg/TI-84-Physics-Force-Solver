#!/usr/bin/env python3
"""
FORCES.8xg builder -- physics force-solver suite for the TI-84 Plus CE.

This script holds the complete TI-BASIC source of every program in the suite,
tokenizes each program with the `tivars` library, and packs all of them into a
single calculator group file, FORCES.8xg, in the current directory.

    pip install tivars
    python forces_builder.py

Programs in the group (all names are 8 characters or fewer):

    FORCEMNU   master menu / launcher
    GSET       gravity setup, stores g in the shared variable G
    VECADD     2-D vector addition, three input modes
    FLATFRC    horizontal-surface force solver
    ANGPULL    force applied above or below the horizontal
    RAMPSLV    inclined-plane solver
    FBDHELP    multi-page free-body-diagram reference

Shared calculator variables
---------------------------
    G          gravitational acceleration (m/s^2), default 9.8
    L1 .. L4   vector component / magnitude / angle lists used by VECADD

Design rules enforced by validate_sources() below
-------------------------------------------------
    * program names <= 8 characters, letters and digits, starting with a letter
    * every Goto and every Menu( label target exists in the same program
    * every prgmNAME call names a program in this group
    * If/Then/End balanced
    * Output( rows within 1..10 and columns within 1..26
    * string literals short enough to fit the 26-column CE screen
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

GROUP_NAME = "FORCES"
GROUP_FILE = "FORCES.8xg"

# ---------------------------------------------------------------------------
# TI-BASIC source
# ---------------------------------------------------------------------------
# Every token these programs use is spelled with the "accessible" name from
# the TI-Toolkit token sheet (8X.xml), which is what tivars' tokenizer matches:
#
#   If Then Else End While Repeat For( Return Stop Lbl Goto Pause Input
#   Prompt Disp Output( Menu( ClrHome Degree Float prgm
#   sqrt( tan^-1( sin( cos( sin( abs( round( min( max( fPart( int( not(
#   ->  >=  <=  !=
#
# Tokens that carry a trailing space in the token sheet (Disp, If, Lbl, Goto,
# Pause, Input, Prompt, While, Repeat) are always followed by their argument
# here, so no line ever ends in a space.
# ---------------------------------------------------------------------------

FORCEMNU = """\
ClrHome
Degree
Full
Float
If G<=0
9.8->G
Lbl 1
ClrHome
Menu("FORCE SOLVER","1 GRAVITY SETUP",2,"2 VECTOR ADD",3,"3 HORIZONTAL",4,"4 ANGLED FORCE",5,"5 INCLINED PLANE",6,"6 FBD HELP",7,"7 EXIT",8)
Lbl 2
prgmGSET
Goto 1
Lbl 3
prgmVECADD
Goto 1
Lbl 4
prgmFLATFRC
Goto 1
Lbl 5
prgmANGPULL
Goto 1
Lbl 6
prgmRAMPSLV
Goto 1
Lbl 7
prgmFBDHELP
Goto 1
Lbl 8
ClrHome
Degree
Float
Output(1,1,"GOODBYE")
Stop
"""

GSET = """\
ClrHome
Degree
Full
If G<=0
9.8->G
Output(1,1,"GRAVITY SETUP")
Output(3,1,"CURRENT g")
Output(3,11,round(G,3))
Output(4,1,"m/s2")
Output(6,1,"PICK A VALUE")
Menu("GRAVITY","9.8 m/s2",2,"9.81 m/s2",3,"10 m/s2",4,"CUSTOM",5,"CANCEL",9)
Lbl 2
9.8->G
Goto 6
Lbl 3
9.81->G
Goto 6
Lbl 4
10->G
Goto 6
Lbl 5
ClrHome
Output(1,1,"CUSTOM GRAVITY")
Output(3,1,"ENTER g IN m/s2")
Input "g=",W
If W<=0
Then
Output(5,1,"MUST BE POSITIVE")
Pause "RETRY"
Goto 5
End
W->G
Lbl 6
ClrHome
Output(1,1,"g IS NOW")
Output(2,1,round(G,3))
Output(3,1,"m/s2")
Output(5,1,"USED BY ALL")
Output(6,1,"SOLVERS")
Pause "DONE"
Goto 9
Lbl 9
Degree
Return
"""


VECADD = """\
ClrHome
Degree
Full
Lbl 1
ClrHome
Menu("VECTOR ADDITION","MAG + ANGLE",10,"X AND Y PARTS",20,"N S E W TOTALS",30)
Lbl 10
ClrHome
Output(1,1,"HOW MANY FORCES?")
Output(2,1,"1 TO 20")
Input "N=",N
If N<1
Then
Output(4,1,"BAD VALUE")
Pause "RETRY"
Goto 10
End
If N>20
Then
Output(4,1,"BAD VALUE")
Pause "RETRY"
Goto 10
End
N->dim(L1)
N->dim(L2)
N->dim(L3)
N->dim(L4)
1->I
Lbl 11
ClrHome
Output(1,1,"VECTOR")
Output(1,8,I)
Output(1,12,"OF")
Output(1,16,N)
Output(3,1,"MAGNITUDE (N)")
Input "F=",F
If F<0
Then
Output(5,1,"MUST BE 0 OR MORE")
Pause "RETRY"
Goto 11
End
F->L3(I)
Lbl 13
Output(6,1,"ANGLE deg 0-360")
Input "A=",W
If W<0
Then
Output(8,1,"MUST BE 0 TO 360")
Pause "RETRY"
Goto 13
End
If W>360
Then
Output(8,1,"MUST BE 0 TO 360")
Pause "RETRY"
Goto 13
End
W->L4(I)
I+1->I
If I<=N
Goto 11
0->X
0->Y
1->I
Lbl 12
L3(I)*cos(L4(I))->L1(I)
L3(I)*sin(L4(I))->L2(I)
X+L1(I)->X
Y+L2(I)->Y
I+1->I
If I<=N
Goto 12
1->Z
Goto 40
Lbl 20
ClrHome
Output(1,1,"HOW MANY FORCES?")
Output(2,1,"X AND Y PARTS")
Input "N=",N
If N<1
Then
Output(4,1,"BAD VALUE")
Pause "RETRY"
Goto 20
End
If N>20
Then
Output(4,1,"BAD VALUE")
Pause "RETRY"
Goto 20
End
N->dim(L1)
N->dim(L2)
1->I
Lbl 21
ClrHome
Output(1,1,"VECTOR")
Output(1,8,I)
Output(1,12,"OF")
Output(1,16,N)
Output(3,1,"X PART (N)")
Input "Fx=",W
W->L1(I)
Output(5,1,"Y PART (N)")
Input "Fy=",W
W->L2(I)
I+1->I
If I<=N
Goto 21
0->X
0->Y
1->I
Lbl 22
X+L1(I)->X
Y+L2(I)->Y
I+1->I
If I<=N
Goto 22
1->Z
Goto 40
Lbl 30
ClrHome
Output(1,1,"TOTALS BY")
Output(2,1,"DIRECTION")
Output(3,1,"FORCES IN N")
Output(4,1,"EACH 0 OR MORE")
Lbl 35
Input "NORTH=",Q
If Q<0
Then
Output(8,1,"MUST BE 0 OR MORE")
Pause "RETRY"
Goto 35
End
Lbl 36
Input "SOUTH=",R
If R<0
Then
Output(8,1,"MUST BE 0 OR MORE")
Pause "RETRY"
Goto 36
End
Lbl 37
Input "EAST=",S
If S<0
Then
Output(8,1,"MUST BE 0 OR MORE")
Pause "RETRY"
Goto 37
End
Lbl 38
Input "WEST=",U
If U<0
Then
Output(8,1,"MUST BE 0 OR MORE")
Pause "RETRY"
Goto 38
End
S-U->X
Q-R->Y
0->Z
Lbl 40
If Z=0
Goto 42
1->I
Lbl 41
ClrHome
Output(1,1,"COMPONENTS (N)")
Output(2,1,"VECTOR")
Output(2,8,I)
Output(2,11,"OF")
Output(2,14,N)
Output(3,1,"SIGNED X AND Y")
Output(4,1,"Fx")
Output(4,4,round(L1(I),2))
Output(5,1,"Fy")
Output(5,4,round(L2(I),2))
If L1(I)>0
Output(4,15,"E")
If L1(I)<0
Output(4,15,"W")
If L2(I)>0
Output(5,15,"N")
If L2(I)<0
Output(5,15,"S")
Pause "NEXT"
I+1->I
If I<=N
Goto 41
Lbl 42
ClrHome
Output(1,1,"VECTOR SUM (N)")
Output(3,1,"Sum Fx")
Output(3,8,round(X,2))
Output(4,1,"Sum Fy")
Output(4,8,round(Y,2))
If X>0
Output(3,18,"E")
If X<0
Output(3,18,"W")
If Y>0
Output(4,18,"N")
If Y<0
Output(4,18,"S")
Output(6,1,"EAST (N)")
Output(6,11,round(max(X,0),2))
Output(7,1,"WEST (N)")
Output(7,11,round(max(-X,0),2))
Output(8,1,"NORTH (N)")
Output(8,11,round(max(Y,0),2))
Output(9,1,"SOUTH (N)")
Output(9,11,round(max(-Y,0),2))
Pause "NEXT"
sqrt(X*X+Y*Y)->R
ClrHome
Output(1,1,"RESULTANT")
Output(3,1,"R (N)")
Output(3,10,round(R,2))
If R<0.00001
Goto 50
If X=0
Then
270->P
If Y>0
90->P
Goto 43
End
tan^-1(Y/X)->P
If X<0
P+180->P
If X>0
Then
If Y<0
P+360->P
End
Lbl 43
Output(4,1,"ANGLE deg")
Output(4,13,round(P,2))
P->T
If T>=360
T-360->T
fPart(T/90)*90->U
min(U,90-U)->V
Output(5,1,"REF ANGLE")
Output(5,13,round(V,2))
round(T/90)->K
If K=4
0->K
If K=0
Output(6,1,"FROM EAST AXIS")
If K=1
Output(6,1,"FROM NORTH AXIS")
If K=2
Output(6,1,"FROM WEST AXIS")
If K=3
Output(6,1,"FROM SOUTH AXIS")
Pause "NEXT"
P+180->E
If E>=360
E-360->E
ClrHome
Output(1,1,"EQUILIBRANT")
Output(3,1,"E (N)")
Output(3,10,round(R,2))
Output(4,1,"ANGLE deg")
Output(4,13,round(E,2))
Output(6,1,"OPPOSITE OF R")
Pause "DONE"
Goto 60
Lbl 50
ClrHome
Output(1,1,"RESULTANT")
Output(2,1,"IS ZERO")
Output(4,1,"FORCES BALANCE")
Output(5,1,"SYSTEM IS IN")
Output(6,1,"EQUILIBRIUM")
Output(8,1,"NO ANGLE EXISTS")
Pause "DONE"
Lbl 60
Menu("AGAIN","NEW PROBLEM",61,"MAIN MENU",62)
Lbl 61
Goto 1
Lbl 62
Return
"""

FLATFRC = """\
ClrHome
Degree
Full
If G<=0
9.8->G
Lbl 1
ClrHome
Output(1,1,"HORIZONTAL SURFACE")
Output(3,1,"MASS (kg)")
Input "M=",M
If M>0
Goto 2
Output(5,1,"MASS MUST BE")
Output(6,1,"MORE THAN ZERO")
Pause "RETRY"
Goto 1
Lbl 2
ClrHome
Output(1,1,"APPLIED FORCE")
Output(2,1,"HORIZONTAL, IN N")
Input "F=",F
If F>=0
Goto 3
Output(5,1,"MUST BE 0 OR MORE")
Pause "RETRY"
Goto 2
Lbl 3
ClrHome
Menu("FORCE DIRECTION","RIGHT",4,"LEFT",5)
Lbl 4
1->D
Goto 6
Lbl 5
-1->D
Lbl 6
ClrHome
Menu("STATE OF MOTION","AT REST",7,"CONSTANT VEL",8,"ACCELERATING",9)
Lbl 7
1->Q
Goto 10
Lbl 8
2->Q
Goto 10
Lbl 9
3->Q
Lbl 10
1->R
If Q=1
Goto 41
If Q=3
Goto 40
Goto 41
Lbl 40
ClrHome
Menu("MOVING WHICH WAY?","SAME AS PUSH",42,"OPPOSITE",43)
Lbl 42
1->R
Goto 41
Lbl 43
-1->R
Lbl 41
ClrHome
Menu("STATIC MU","KNOWN",11,"ZERO",12,"UNKNOWN",13)
Lbl 11
Input "Mu s=",S
If S>=0
Goto 14
Output(5,1,"MUST BE 0 OR MORE")
Pause "RETRY"
Goto 11
Lbl 12
0->S
Lbl 14
1->P
Goto 15
Lbl 13
0->P
Lbl 15
ClrHome
Menu("KINETIC MU","KNOWN",16,"ZERO",17,"UNKNOWN",18)
Lbl 16
Input "Mu k=",K
If K>=0
Goto 19
Output(5,1,"MUST BE 0 OR MORE")
Pause "RETRY"
Goto 16
Lbl 17
0->K
Lbl 19
1->J
Goto 20
Lbl 18
0->J
Lbl 20
M*G->W
W->N
F*D->A
S*N->C
K*N->E
ClrHome
Output(1,1,"HORIZONTAL FORCES")
Output(2,1,"MASS (kg)")
Output(2,10,round(M,2))
Output(3,1,"PUSH (N)")
Output(3,10,round(F,2))
Output(4,1,"WEIGHT (N)")
Output(4,11,round(W,2))
Output(5,1,"NORMAL (N)")
Output(5,11,round(N,2))
If P=1
Output(6,1,"Fs max (N)")
If P=1
Output(6,11,round(C,2))
If P=0
Output(6,1,"Fs max UNKNOWN")
If J=1
Output(7,1,"Fk (N)")
If J=1
Output(7,11,round(E,2))
If J=0
Output(7,1,"Fk UNKNOWN")
Output(8,1,"g (m/s2)")
Output(8,11,round(G,3))
Pause "NEXT"
If Q=1
Goto 21
If Q=2
Goto 22
Goto 23
Lbl 21
ClrHome
Output(1,1,"AT REST CHECK")
If F=0
Then
Output(3,1,"NO PUSH APPLIED")
Output(5,1,"STAYS AT REST")
Goto 30
End
If P=0
Then
Output(3,1,"STATIC MU NEEDED")
Output(5,1,"REQUIRED Fs (N)")
Output(5,17,round(F,2))
Goto 30
End
If F<=C
Then
Output(3,1,"CAN STAY AT REST")
Output(4,1,"Fs needed (N)")
Output(4,15,round(F,2))
Output(5,1,"Fs max (N)")
Output(5,15,round(C,2))
If D=1
Output(7,1,"FRICTION POINTS LEFT")
If D=-1
Output(7,1,"FRICTION POINTS RIGHT")
Goto 30
End
Output(3,1,"STATIC EQUILIBRIUM")
Output(4,1,"IS IMPOSSIBLE")
Output(5,1,"Fs max (N)")
Output(5,15,round(C,2))
Output(6,1,"Fs needed (N)")
Output(6,15,round(F,2))
If J=0
Then
Output(8,1,"KINETIC MU NEEDED")
Output(9,1,"TO FIND ACCELERATION")
Goto 30
End
Pause "NEXT"
Goto 23
Lbl 22
ClrHome
Output(1,1,"CONSTANT VELOCITY")
Output(3,1,"NET FORCE MUST BE 0")
Output(5,1,"Fk needed (N)")
Output(5,15,round(F,2))
Output(6,1,"Mu k needed")
Output(6,15,round(F/N,2))
Output(7,1,"MOTION IS ALONG PUSH")
If J=0
Then
Output(8,1,"ENTER THIS MU K")
Output(9,1,"FOR THAT MOTION")
Goto 30
End
If abs(E-F)<=0.05
Then
Output(8,1,"MU K IS CONSISTENT")
Goto 30
End
Output(8,1,"MU K DOES NOT FIT")
Output(9,1,"Fk from mu k:")
Output(9,17,round(E,2))
Goto 30
Lbl 23
ClrHome
Output(1,1,"ACCELERATING")
If J=0
Then
Output(3,1,"KINETIC MU NEEDED")
Output(5,1,"WITHOUT IT THE")
Output(6,1,"FRICTION IS UNKNOWN")
Goto 30
End
Output(3,1,"Fk (N)")
Output(3,8,round(E,2))
D*(F-R*E)->U
U/M->V
Output(4,1,"Fnet (N)")
Output(4,10,round(U,2))
Output(6,1,"a (m/s2)")
Output(6,11,round(V,2))
If V=0
Output(8,1,"ZERO ACCELERATION")
If V*D>0
Output(8,1,"a IS SAME AS PUSH")
If V*D<0
Output(8,1,"a IS OPPOSITE PUSH")
If V*D*R>0
Output(9,1,"SPEEDING UP")
If V*D*R<0
Output(9,1,"SLOWING DOWN")
Lbl 30
Pause "DONE"
Menu("AGAIN","NEW PROBLEM",31,"MAIN MENU",32)
Lbl 31
Goto 1
Lbl 32
Return
"""


ANGPULL = """\
ClrHome
Degree
Full
If G<=0
9.8->G
Lbl 1
ClrHome
Output(1,1,"ANGLED FORCE")
Output(3,1,"MASS (kg)")
Input "M=",M
If M>0
Goto 2
Output(5,1,"MASS MUST BE")
Output(6,1,"MORE THAN ZERO")
Pause "RETRY"
Goto 1
Lbl 2
ClrHome
Output(1,1,"ANGLE FROM")
Output(2,1,"HORIZONTAL, deg")
Output(3,1,"0 TO 90")
Input "A=",T
If T>=0
Goto 3
Output(5,1,"MUST BE 0 TO 90")
Pause "RETRY"
Goto 2
Lbl 3
If T<=90
Goto 4
Output(5,1,"MUST BE 0 TO 90")
Pause "RETRY"
Goto 2
Lbl 4
ClrHome
Menu("FORCE POINTS","UP",5,"DOWN",6)
Lbl 5
1->U
Goto 7
Lbl 6
-1->U
Lbl 7
ClrHome
Menu("HORIZONTAL DIR","RIGHT",8,"LEFT",9)
Lbl 8
1->D
Goto 10
Lbl 9
-1->D
Lbl 10
ClrHome
Menu("WHAT TO SOLVE?","ACCEL FROM F",11,"FORCE FOR EQ",12)
Lbl 11
ClrHome
Output(1,1,"APPLIED FORCE (N)")
Input "F=",F
If F>=0
Goto 13
Output(5,1,"MUST BE 0 OR MORE")
Pause "RETRY"
Goto 11
Lbl 13
ClrHome
Menu("STATE OF MOTION","AT REST",14,"CONSTANT VEL",15,"ACCELERATING",16)
Lbl 14
1->Q
Goto 17
Lbl 15
2->Q
Goto 17
Lbl 16
3->Q
Lbl 17
ClrHome
Menu("STATIC MU","KNOWN",18,"UNKNOWN",19)
Lbl 18
Input "Mu s=",S
If S>=0
Goto 20
Output(5,1,"MUST BE 0 OR MORE")
Pause "RETRY"
Goto 18
Lbl 20
1->P
Goto 21
Lbl 19
0->P
Lbl 21
ClrHome
Menu("KINETIC MU","KNOWN",22,"UNKNOWN",23)
Lbl 22
Input "Mu k=",K
If K>=0
Goto 24
Output(5,1,"MUST BE 0 OR MORE")
Pause "RETRY"
Goto 22
Lbl 24
1->J
Goto 30
Lbl 23
0->J
Lbl 30
1->R
If Q=1
Goto 32
If Q=3
Goto 31
Goto 32
Lbl 31
ClrHome
Menu("MOVING WHICH WAY?","SAME AS Fx",33,"OPPOSITE",34)
Lbl 33
1->R
Goto 32
Lbl 34
-1->R
Lbl 32
M*G->W
F*cos(T)->H
U*F*sin(T)->V
W-V->N
ClrHome
Output(1,1,"ANGLED FORCE")
Output(2,1,"MASS (kg)")
Output(2,10,round(M,2))
Output(3,1,"F (N)")
Output(3,10,round(F,2))
Output(4,1,"ANGLE deg")
Output(4,13,round(T,2))
Output(5,1,"WEIGHT (N)")
Output(5,13,round(W,2))
Output(6,1,"Fx (N)")
Output(6,10,round(H,2))
Output(7,1,"Fy (N)")
Output(7,10,round(V,2))
Output(8,1,"NORMAL (N)")
Output(8,13,round(N,2))
Pause "NEXT"
If N<=0
Goto 40
S*N->C
K*N->E
If Q=1
Goto 50
If Q=2
Goto 60
Goto 70
Lbl 40
ClrHome
Output(1,1,"NORMAL FORCE IS")
Output(2,1,"ZERO OR LESS")
Output(4,1,"OBJECT LEAVES")
Output(5,1,"THE SURFACE")
Output(6,1,"NO FRICTION ACTS")
D*H/M->A
Output(8,1,"a (m/s2)")
Output(8,11,round(A,2))
Pause "DONE"
Goto 80
Lbl 50
ClrHome
Output(1,1,"AT REST CHECK")
If F=0
Then
Output(3,1,"NO FORCE APPLIED")
Output(5,1,"STAYS AT REST")
Goto 80
End
If P=0
Then
Output(3,1,"STATIC MU NEEDED")
Output(5,1,"REQUIRED Fs (N)")
Output(5,17,round(H,2))
Goto 80
End
If H<=C
Then
Output(3,1,"CAN STAY AT REST")
Output(4,1,"Fs needed (N)")
Output(4,15,round(H,2))
Output(5,1,"Fs max (N)")
Output(5,15,round(C,2))
If D=1
Output(7,1,"FRICTION POINTS LEFT")
If D=-1
Output(7,1,"FRICTION POINTS RIGHT")
Goto 80
End
Output(3,1,"STATIC EQUILIBRIUM")
Output(4,1,"IS IMPOSSIBLE")
Output(5,1,"Fs max (N)")
Output(5,15,round(C,2))
Output(6,1,"Fs needed (N)")
Output(6,15,round(H,2))
If J=0
Then
Output(8,1,"KINETIC MU NEEDED")
Output(9,1,"TO FIND ACCELERATION")
Goto 80
End
Pause "NEXT"
Goto 70
Lbl 60
ClrHome
Output(1,1,"CONSTANT VELOCITY")
Output(3,1,"NET FORCE MUST BE 0")
Output(5,1,"Fk needed (N)")
Output(5,15,round(H,2))
Output(6,1,"Mu k needed")
Output(6,15,round(H/N,2))
Output(7,1,"MOTION IS ALONG Fx")
If J=0
Then
Output(8,1,"ENTER THIS MU K")
Output(9,1,"FOR THAT MOTION")
Goto 80
End
If abs(E-H)<=0.05
Then
Output(8,1,"MU K IS CONSISTENT")
Goto 80
End
Output(8,1,"MU K DOES NOT FIT")
Output(9,1,"Fk from mu k:")
Output(9,17,round(E,2))
Goto 80
Lbl 70
ClrHome
Output(1,1,"ACCELERATING")
If J=0
Then
Output(3,1,"KINETIC MU NEEDED")
Output(5,1,"WITHOUT IT THE")
Output(6,1,"FRICTION IS UNKNOWN")
Goto 80
End
Output(3,1,"Fk (N)")
Output(3,8,round(E,2))
D*(H-R*E)->A
A/M->B
Output(4,1,"Fnet (N)")
Output(4,10,round(A,2))
Output(6,1,"a (m/s2)")
Output(6,11,round(B,2))
If B=0
Output(8,1,"ZERO ACCELERATION")
If B*D>0
Output(8,1,"a IS SAME AS Fx")
If B*D<0
Output(8,1,"a IS OPPOSITE Fx")
If B*D*R>0
Output(9,1,"SPEEDING UP")
If B*D*R<0
Output(9,1,"SLOWING DOWN")
Goto 80
Lbl 80
Pause "DONE"
Menu("AGAIN","NEW PROBLEM",81,"MAIN MENU",82)
Lbl 81
Goto 1
Lbl 82
Return
Lbl 12
ClrHome
Output(1,1,"FORCE FOR")
Output(2,1,"EQUILIBRIUM")
Menu("FRICTION TYPE","STATIC",83,"KINETIC",84)
Lbl 83
Input "Mu s=",S
If S>=0
Goto 85
Output(5,1,"MUST BE 0 OR MORE")
Pause "RETRY"
Goto 83
Lbl 85
1->P
Goto 87
Lbl 84
Input "Mu k=",S
If S>=0
Goto 86
Output(5,1,"MUST BE 0 OR MORE")
Pause "RETRY"
Goto 84
Lbl 86
0->P
Lbl 87
M*G->W
cos(T)+U*S*sin(T)->A
If A<=0
Goto 88
S*W/A->F
W-U*F*sin(T)->N
If N<=0
Goto 88
ClrHome
Output(1,1,"NEEDED APPLIED F")
Output(3,1,"F (N)")
Output(3,10,round(F,2))
Output(4,1,"MU USED")
Output(4,11,round(S,2))
Output(5,1,"ANGLE deg")
Output(5,13,round(T,2))
Output(6,1,"NORMAL (N)")
Output(6,13,round(N,2))
Output(8,1,"Fx (N)")
Output(8,10,round(F*cos(T),2))
Goto 89
Lbl 88
ClrHome
Output(1,1,"NO SOLUTION")
Output(3,1,"NO APPLIED FORCE")
Output(4,1,"CAN HOLD THIS")
Output(5,1,"OBJECT AT REST")
Output(7,1,"PUSHING HARDER")
Output(8,1,"ADDS MORE FRICTION")
Lbl 89
Pause "DONE"
Menu("AGAIN","NEW PROBLEM",81,"MAIN MENU",82)
"""

RAMPSLV = """\
ClrHome
Degree
Full
If G<=0
9.8->G
Lbl 1
ClrHome
Output(1,1,"INCLINED PLANE")
Output(3,1,"MASS (kg)")
Input "M=",M
If M>0
Goto 2
Output(5,1,"MASS MUST BE")
Output(6,1,"MORE THAN ZERO")
Pause "RETRY"
Goto 1
Lbl 2
ClrHome
Output(1,1,"RAMP ANGLE, deg")
Output(2,1,"MORE THAN 0")
Output(3,1,"LESS THAN 90")
Input "A=",T
If T>0
Goto 3
Output(5,1,"MUST BE ABOVE 0")
Pause "RETRY"
Goto 2
Lbl 3
If T<90
Goto 4
Output(5,1,"MUST BE BELOW 90")
Pause "RETRY"
Goto 2
Lbl 4
ClrHome
Output(1,1,"FORCE ALONG RAMP")
Output(2,1,"IN N, 0 IF NONE")
Input "F=",F
If F>=0
Goto 5
Output(5,1,"MUST BE 0 OR MORE")
Pause "RETRY"
Goto 4
Lbl 5
ClrHome
Menu("FORCE DIRECTION","UP RAMP",6,"DOWN RAMP",7)
Lbl 6
1->U
Goto 8
Lbl 7
-1->U
Lbl 8
ClrHome
Menu("MOTION STATE","AT REST",9,"MOVING UP",10,"MOVING DOWN",11)
Lbl 9
1->Q
0->R
Goto 12
Lbl 10
2->Q
1->R
Goto 12
Lbl 11
3->Q
-1->R
Lbl 12
ClrHome
Menu("STATIC MU","KNOWN",13,"UNKNOWN",14)
Lbl 13
Input "Mu s=",S
If S>=0
Goto 15
Output(5,1,"MUST BE 0 OR MORE")
Pause "RETRY"
Goto 13
Lbl 15
1->P
Goto 16
Lbl 14
0->P
Lbl 16
ClrHome
Menu("KINETIC MU","KNOWN",17,"UNKNOWN",18)
Lbl 17
Input "Mu k=",K
If K>=0
Goto 19
Output(5,1,"MUST BE 0 OR MORE")
Pause "RETRY"
Goto 17
Lbl 19
1->J
Goto 30
Lbl 18
0->J
Lbl 30
M*G->W
W*sin(T)->H
W*cos(T)->V
V->N
S*N->C
K*N->E
ClrHome
Output(1,1,"INCLINED PLANE")
Output(2,1,"MASS (kg)")
Output(2,10,round(M,2))
Output(3,1,"ANGLE deg")
Output(3,13,round(T,2))
Output(4,1,"WEIGHT (N)")
Output(4,13,round(W,2))
Output(5,1,"ALONG RAMP (N)")
Output(5,16,round(H,2))
Output(6,1,"INTO RAMP (N)")
Output(6,16,round(V,2))
Output(7,1,"NORMAL (N)")
Output(7,13,round(N,2))
Output(8,1,"APPLIED (N)")
Output(8,13,round(F,2))
Pause "NEXT"
If Q=1
Goto 40
Goto 60
Lbl 40
ClrHome
Output(1,1,"AT REST CHECK")
F*U-H->B
If B>0
Then
Output(3,1,"TENDENCY TO MOVE")
Output(4,1,"UP THE RAMP")
End
If B<0
Then
Output(3,1,"TENDENCY TO MOVE")
Output(4,1,"DOWN THE RAMP")
End
If B=0
Then
Output(3,1,"NO TENDENCY TO")
Output(4,1,"SLIDE AT ALL")
Output(6,1,"STAYS AT REST")
Goto 55
End
abs(B)->A
Output(6,1,"Fs needed (N)")
Output(6,15,round(A,2))
If P=0
Then
Output(8,1,"STATIC MU NEEDED")
Output(9,1,"TO DECIDE")
Goto 55
End
If A<=C
Then
Output(8,1,"STAYS AT REST")
Output(9,1,"Fs max (N)")
Output(9,14,round(C,2))
Goto 55
End
Output(8,1,"SLIDES: FS MAX")
Output(9,1,"IS TOO SMALL")
Pause "NEXT"
If J=0
Then
ClrHome
Output(1,1,"KINETIC MU NEEDED")
Output(3,1,"TO FIND MOTION")
Goto 55
End
2->Q
1->R
If B<0
-1->R
Goto 60
Lbl 60
ClrHome
Output(1,1,"SLIDING ON RAMP")
If R>0
Output(2,1,"MOVING UP THE RAMP")
If R<0
Output(2,1,"MOVING DOWN RAMP")
If J=0
Then
Output(4,1,"KINETIC MU NEEDED")
Output(5,1,"CANNOT FIND a")
Goto 55
End
F*U-H-R*E->A
A/M->B
Output(4,1,"Fk (N)")
Output(4,9,round(E,2))
Output(5,1,"Fnet (N)")
Output(5,10,round(A,2))
Output(7,1,"a (m/s2)")
Output(7,11,round(B,2))
If B>0
Output(9,1,"a POINTS UP RAMP")
If B<0
Output(9,1,"a POINTS DOWN RAMP")
If B=0
Output(9,1,"a IS ZERO")
Goto 55
Lbl 55
If P=1
Then
tan^-1(S)->A
Output(10,1,"Crit angle deg")
Output(10,17,round(A,2))
End
Pause "DONE"
Menu("AGAIN","NEW PROBLEM",56,"MAIN MENU",57)
Lbl 56
Goto 1
Lbl 57
Return
"""


FBDHELP = """\
ClrHome
Degree
Full
Lbl 1
ClrHome
Menu("FREE BODY HELP","FORCE SYMBOLS",2,"FRICTION",3,"ANGLED FORCE",4,"ON A RAMP",5,"EQUILIBRIUM",6,"NEWTON LAWS",7,"QUIT",8)
Lbl 2
ClrHome
Output(1,1,"FORCE SYMBOLS")
Output(2,1,"Fg weight = M * G")
Output(3,1,"FN normal: surface")
Output(4,1,"  pushes perpendicular")
Output(5,1,"FT tension: rope pulls")
Output(6,1,"  away from object")
Output(7,1,"Fapp: push or pull")
Output(8,1,"Ffs static friction")
Output(9,1,"Ffk kinetic friction")
Pause "NEXT"
ClrHome
Output(1,1,"MASS AND WEIGHT")
Output(3,1,"Mass M in kg is the")
Output(4,1,"amount of matter.")
Output(6,1,"Weight Fg in N is the")
Output(7,1,"force of gravity:")
Output(9,1,"Fg = M * G")
Pause "BACK"
Goto 1
Lbl 3
ClrHome
Output(1,1,"FRICTION")
Output(2,1,"Static friction holds")
Output(3,1,"an object at rest.")
Output(4,1,"Ffs max = Mu s * FN")
Output(6,1,"Kinetic friction acts")
Output(7,1,"while sliding:")
Output(8,1,"Ffk = Mu k * FN")
Output(9,1,"Mu k is below Mu s.")
Pause "NEXT"
ClrHome
Output(1,1,"FRICTION DIAGRAM")
Output(3,1,"    Fapp -->")
Output(4,1,"   [BLOCK]")
Output(5,1,"    Ff <--")
Output(7,1,"Ff acts against the")
Output(8,1,"motion, or against the")
Output(9,1,"push if nothing moves.")
Pause "BACK"
Goto 1
Lbl 4
ClrHome
Output(1,1,"ANGLED FORCE")
Output(2,1,"F at angle T above")
Output(3,1,"the horizontal:")
Output(5,1,"Fx = F * cos(T)")
Output(6,1,"Fy = F * sin(T)")
Output(8,1,"Pulling up shrinks FN")
Output(9,1,"FN = Fg - Fy")
Pause "NEXT"
ClrHome
Output(1,1,"ANGLED FORCE 2")
Output(2,1,"Pushing down grows FN")
Output(3,1,"FN = Fg + Fy")
Output(5,1,"If FN reaches 0 the")
Output(6,1,"object leaves the")
Output(7,1,"surface and friction")
Output(8,1,"disappears.")
Pause "BACK"
Goto 1
Lbl 5
ClrHome
Output(1,1,"ON A RAMP")
Output(2,1,"Fg down the slope:")
Output(3,1,"Fg * sin(T)")
Output(4,1,"Fg into the slope:")
Output(5,1,"Fg * cos(T) = FN")
Output(7,1,"Friction opposes the")
Output(8,1,"actual or impending")
Output(9,1,"motion, NOT always")
Output(10,1,"down the ramp.")
Pause "BACK"
Goto 1
Lbl 6
ClrHome
Output(1,1,"EQUILIBRIUM")
Output(3,1,"Sum Fx = 0")
Output(4,1,"Sum Fy = 0")
Output(6,1,"True at rest AND at")
Output(7,1,"constant velocity.")
Output(9,1,"Net force 0 means the")
Output(10,1,"acceleration is 0.")
Pause "BACK"
Goto 1
Lbl 7
ClrHome
Output(1,1,"NEWTON LAW 1")
Output(3,1,"No net force: an")
Output(4,1,"object stays at rest")
Output(5,1,"or keeps a constant")
Output(6,1,"velocity.")
Pause "NEXT"
ClrHome
Output(1,1,"NEWTON LAW 2")
Output(3,1,"Fnet = M * a")
Output(5,1,"a = Fnet / M")
Output(7,1,"a points the same way")
Output(8,1,"as the net force.")
Pause "NEXT"
ClrHome
Output(1,1,"NEWTON LAW 3")
Output(3,1,"Forces act in pairs,")
Output(4,1,"equal and opposite,")
Output(5,1,"on two DIFFERENT")
Output(6,1,"objects.")
Output(8,1,"Book pushes on table;")
Output(9,1,"table pushes on book.")
Pause "BACK"
Goto 1
Lbl 8
ClrHome
Degree
Float
Output(1,1,"HELP CLOSED")
Pause "DONE"
Return
"""

# ---------------------------------------------------------------------------
# Program table
# ---------------------------------------------------------------------------

PROGRAM_INFO = {
    "FORCEMNU": "master menu and launcher",
    "GSET": "gravity setup, stores g in G",
    "VECADD": "2-D vector addition (3 input modes)",
    "FLATFRC": "horizontal-surface force solver",
    "ANGPULL": "force above or below the horizontal",
    "RAMPSLV": "inclined-plane solver",
    "FBDHELP": "free-body-diagram reference",
}

PROGRAMS = {
    "FORCEMNU": FORCEMNU,
    "GSET": GSET,
    "VECADD": VECADD,
    "FLATFRC": FLATFRC,
    "ANGPULL": ANGPULL,
    "RAMPSLV": RAMPSLV,
    "FBDHELP": FBDHELP,
}

ORDER = ["FORCEMNU", "GSET", "VECADD", "FLATFRC", "ANGPULL", "RAMPSLV", "FBDHELP"]

# ---------------------------------------------------------------------------
# Static validation of the TI-BASIC sources
# ---------------------------------------------------------------------------

NAME_RE = re.compile(r"^[A-Z][A-Z0-9]{0,7}$")
LABEL_RE = re.compile(r"^[A-Za-z0-9\u03b8]{1,2}$")
OUTPUT_RE = re.compile(r"^Output\((\d+),(\d+),(.+)\)$")
INPUT_PROMPT_RE = re.compile(r'^Input "([^"]*)",')

# Screen geometry of the TI-84 Plus CE home screen in the large font.
MAX_ROW = 10
MAX_COL = 26
MAX_MENU_ITEM = 24   # item text limit on the color models
MAX_INPUT_PROMPT = 20
# Widest a number can be once printed in Float mode (sign included), which is
# what every numeric Output( in these sources produces via round(x,2).
VALUE_WIDTH = 10

BARE_TOKEN_ERRORS = {
    "Disp": "Disp needs an argument (the token is spelled 'Disp ')",
    "If": "If needs a condition (the token is spelled 'If ')",
    "Lbl": "Lbl needs a name (the token is spelled 'Lbl ')",
    "Goto": "Goto needs a name (the token is spelled 'Goto ')",
    "Pause": "Pause needs an argument (the token is spelled 'Pause ')",
    "Input": "Input needs a variable",
    "Prompt": "Prompt needs a variable",
}


def clean_source(source: str) -> str:
    """Return the program source with no blank first/last line and no
    trailing whitespace, so no token is left without its argument."""
    lines = [line.rstrip() for line in source.splitlines()]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def _split_menu_args(text: str) -> list:
    args, buf, in_str = [], [], False
    for ch in text:
        if ch == '"':
            in_str = not in_str
            buf.append(ch)
        elif ch == "," and not in_str:
            args.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    args.append("".join(buf).strip())
    return args


def _output_width(argument: str) -> int:
    """How many columns an Output( argument occupies once displayed."""
    argument = argument.strip()
    if len(argument) >= 2 and argument.startswith('"') and argument.endswith('"'):
        return len(argument) - 2
    return VALUE_WIDTH


def validate_sources() -> list:
    """Check every program against the rules the calculator enforces.
    Returns a list of error strings (empty when everything is fine)."""
    errors = []

    for name in ORDER:
        if name not in PROGRAMS:
            errors.append("program %s is listed in ORDER but has no source" % name)
    for name in PROGRAMS:
        if name not in ORDER:
            errors.append("program %s is defined but missing from ORDER" % name)

    for name in ORDER:
        if not NAME_RE.match(name):
            errors.append("%s: invalid program name (max 8 chars, A-Z and 0-9)" % name)
        if len(name) > 8:
            errors.append("%s: program name longer than 8 characters" % name)

    for name in ORDER:
        if name not in PROGRAMS:
            continue
        src = clean_source(PROGRAMS[name])
        where = name

        try:
            src.encode("ascii")
        except UnicodeEncodeError:
            errors.append("%s: source contains a non-ASCII character" % where)

        labels = {}
        gotos = []
        menu_labels = []
        prgm_calls = []
        thens = ends = 0
        for lineno, line in enumerate(src.splitlines(), 1):
            tag = "%s:%d" % (where, lineno)

            if line in BARE_TOKEN_ERRORS:
                errors.append("%s: %s" % (tag, BARE_TOKEN_ERRORS[line]))

            if line.startswith("Lbl "):
                lbl = line[4:].strip()
                if not LABEL_RE.match(lbl):
                    errors.append("%s: invalid label name %r" % (tag, lbl))
                if lbl in labels:
                    errors.append("%s: duplicate Lbl %s (first at line %d)"
                                  % (tag, lbl, labels[lbl]))
                else:
                    labels[lbl] = lineno
            elif line.startswith("Goto "):
                gotos.append((tag, line[5:].strip()))
            elif line.startswith("Menu(") and line.endswith(")"):
                args = _split_menu_args(line[5:-1])
                if (len(args) - 1) % 2 != 0:
                    errors.append("%s: Menu( needs text/label pairs" % tag)
                if args:
                    title = args[0].strip('"')
                    if len(title) > MAX_COL:
                        errors.append("%s: Menu( title %r is %d characters (limit %d)"
                                      % (tag, title, len(title), MAX_COL))
                for text in args[1::2]:
                    item = text.strip('"')
                    if len(item) > MAX_MENU_ITEM:
                        errors.append("%s: Menu( item %r is %d characters (limit %d)"
                                      % (tag, item, len(item), MAX_MENU_ITEM))
                for index in range(2, len(args), 2):
                    menu_labels.append((tag, args[index]))
            elif line.startswith("Input "):
                match = INPUT_PROMPT_RE.match(line)
                if match and len(match.group(1)) > MAX_INPUT_PROMPT:
                    errors.append("%s: Input prompt %r is %d characters (limit %d)"
                                  % (tag, match.group(1), len(match.group(1)),
                                     MAX_INPUT_PROMPT))
            elif line.startswith("Output("):
                match = OUTPUT_RE.match(line)
                if not match:
                    errors.append("%s: malformed Output(" % tag)
                else:
                    row = int(match.group(1))
                    col = int(match.group(2))
                    width = _output_width(match.group(3))
                    if not 1 <= row <= MAX_ROW:
                        errors.append("%s: Output row %d outside 1..%d"
                                      % (tag, row, MAX_ROW))
                    if col < 1:
                        errors.append("%s: Output column %d is before column 1"
                                      % (tag, col))
                    end = col + width - 1
                    if end > MAX_COL:
                        errors.append(
                            "%s: Output(%d,%d,...) reaches column %d, past the %d "
                            "available" % (tag, row, col, end, MAX_COL))

            if line == "Then":
                thens += 1
            elif line == "End":
                ends += 1
                if ends > thens:
                    errors.append("%s: End without Then" % tag)

            for call in re.findall(r"prgm([A-Za-z0-9]+)", line):
                prgm_calls.append((tag, call.upper()))

            for text in re.findall(r'"([^"]*)"', line):
                if len(text) > 26:
                    errors.append("%s: text %r is %d characters (screen is 26)"
                                  % (tag, text, len(text)))

        if thens != ends:
            errors.append("%s: %d Then but %d End" % (where, thens, ends))

        for tag, lbl in gotos:
            if lbl not in labels:
                errors.append("%s: Goto %s has no matching Lbl" % (tag, lbl))
        for tag, lbl in menu_labels:
            if not LABEL_RE.match(lbl):
                errors.append("%s: invalid Menu( label %r" % (tag, lbl))
            elif lbl not in labels:
                errors.append("%s: Menu( label %s has no matching Lbl" % (tag, lbl))
        for tag, call in prgm_calls:
            if call not in PROGRAMS:
                errors.append("%s: prgm%s but that program is not in the group"
                              % (tag, call))

    if "FORCEMNU" in PROGRAMS:
        src = clean_source(PROGRAMS["FORCEMNU"])
        for entry in ("GSET", "VECADD", "FLATFRC", "ANGPULL", "RAMPSLV", "FBDHELP"):
            if "prgm" + entry not in src:
                errors.append("FORCEMNU: menu does not launch prgm%s" % entry)

    return errors


# ---------------------------------------------------------------------------
# Build and verify with tivars
# ---------------------------------------------------------------------------

def build_group(path: Path) -> list:
    """Tokenize every program and pack them into one .8xg group file."""
    try:
        from tivars.models import TI_84PCE
        from tivars.types import TIProgram, TIGroup
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise SystemExit(
            "ERROR: the 'tivars' package is required (%s).\n"
            "Install it with:  pip install tivars" % exc
        )

    entries = []
    for name in ORDER:
        source = clean_source(PROGRAMS[name])
        program = TIProgram(name=name)
        program.load_string(source, model=TI_84PCE)
        if not program.tokens():
            raise SystemExit("ERROR: %s tokenized to nothing" % name)
        entries.append(program)

    group = TIGroup.group(entries, name=GROUP_NAME)
    group.save(str(path), model=TI_84PCE)
    return entries


def _entry_name(entry) -> str:
    try:
        name = entry.name
    except Exception:  # pragma: no cover - defensive
        name = entry.raw.name
    if isinstance(name, bytes):
        name = name.decode("utf-8", "replace")
    return str(name).strip()


def verify_group(path: Path) -> list:
    """Re-open the written group and confirm every program is inside it."""
    from tivars.types import TIGroup

    problems = []
    if not path.exists():
        return ["%s was not written" % path]
    if path.stat().st_size < 55 + 2 * len(ORDER):
        problems.append("%s looks too small to hold %d programs"
                        % (path, len(ORDER)))
    group = TIGroup.open(str(path))
    entries = group.ungroup()
    names = [_entry_name(entry) for entry in entries]
    for name in ORDER:
        if name not in names:
            problems.append("%s missing from the group" % name)
    if len(entries) != len(ORDER):
        problems.append("group holds %d entries, expected %d"
                        % (len(entries), len(ORDER)))
    return problems


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    out_dir = Path(".")

    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    print("Validating TI-BASIC sources ...")
    errors = validate_sources()
    if errors:
        print("FAILED: %d problem(s) in the sources" % len(errors))
        for error in errors:
            print("  - " + error)
        return 1
    print("  ok: %d programs, syntax rules satisfied" % len(ORDER))

    target = out_dir / GROUP_FILE
    print("Tokenizing and packing %s ..." % GROUP_FILE)
    try:
        entries = build_group(target)
    except SystemExit as exc:
        print(exc)
        return 2
    except Exception as exc:  # tokenizer or file error
        print("FAILED while building the group file: %s" % exc)
        return 2

    print("  ok: %d programs tokenized" % len(entries))
    for name in ORDER:
        print("    %-8s  %s" % (name, PROGRAM_INFO[name]))

    problems = verify_group(target)
    if problems:
        print("FAILED: verification of %s" % target)
        for problem in problems:
            print("  - " + problem)
        return 3

    print("Wrote %s (%d bytes)" % (target.resolve(), target.stat().st_size))
    print("Verified: all %d programs are present in the group." % len(ORDER))
    return 0


if __name__ == "__main__":
    sys.exit(main())
