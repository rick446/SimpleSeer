#!/bin/bash

( 
  cd /tmp &&
  hg clone https://bitbucket.org/pygame/pygame &&
  cd pygame &&
  ( 
    patch --verbose --fuzz=10 -p1 <<EOF
--- a/src/scale_mmx64.c
+++ b/src/scale_mmx64.c
@@ -425,7 +425,7 @@
              " movl             %5,      %%ecx;           "
              " pxor          %%mm0,      %%mm0;           "
              "1:                                          "
-             " movsxl         (%3),      %%rax;           " /* get xidx0[x] */
+             " movslq         (%3),      %%rax;           " /* get xidx0[x] */
              " add              $4,         %3;           "
              " movq           (%0),      %%mm1;           " /* load mult0 */
              " add              $8,         %0;           "
@@ -500,7 +500,7 @@
              " movl             %5,      %%ecx;           "
              " pxor          %%mm0,      %%mm0;           "
              "1:                                          "
-             " movsxl         (%3),      %%rax;           " /* get xidx0[x] */
+             " movslq         (%3),      %%rax;           " /* get xidx0[x] */
              " add              $4,         %3;           "
              " movq           (%0),      %%mm1;           " /* load mult0 */
              " add              $8,         %0;           "
EOF
  ) && 
  python setup.py install
) && rm -fr /tmp/pygame