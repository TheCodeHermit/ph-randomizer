; Note - the .fill's are to ensure every entry is padded to 0x1D bytes. This is because the longest
; file name in the Player/get directory is 29 (0x1D) characters long, and we want to be able to
; change these to any given file name during randomization.
;
; TODO: I'm sure ARMIPS offers some feature that let's us do this more elegantly, but
; for now manually specifying the .fill directives will do.
shA_nsbmd:
    .asciiz "Player/get/gd_shA.nsbmd"
    .fill 6, 0
shA_nsbtx:
    .asciiz "Player/get/gd_shA.nsbtx"
    .fill 6, 0
bmbagM_nsbmd:
    .asciiz "Player/get/gd_bmbagM.nsbmd"
    .fill 3, 0
bmbagM_nsbtx:
    .asciiz "Player/get/gd_bmbagM.nsbtx"
    .fill 3, 0
heart_utu_nsbmd:
    .asciiz "Player/get/gd_heart_utu.nsbmd"
    ; No need for padding
heart_utu_nsbtx:
    .asciiz "Player/get/gd_heart_utu.nsbtx"
    ; No need for padding
minaC_nsbmd:
    .asciiz "Player/get/gd_minaC.nsbmd"
    .fill 4, 0
minaC_nsbtx:
    .asciiz "Player/get/gd_minaC.nsbtx"
    .fill 4, 0
minaP_nsbmd:
    .asciiz "Player/get/gd_minaP.nsbmd"
    .fill 4, 0
minaP_nsbtx:
    .asciiz "Player/get/gd_minaP.nsbtx"
    .fill 4, 0
minaY_nsbmd:
    .asciiz "Player/get/gd_minaY.nsbmd"
    .fill 4, 0
minaY_nsbtx:
    .asciiz "Player/get/gd_minaY.nsbtx"
    .fill 4, 0
arrowpod_nsbmd:
    .asciiz "Player/get/gd_arrowpod.nsbmd"
    .fill 1, 0
arrowpod_nsbtx:
    .asciiz "Player/get/gd_arrowpod.nsbtx"
    .fill 1, 0
bcbagM_nsbmd:
    .asciiz "Player/get/gd_bcbagM.nsbmd"
    .fill 3, 0
bcbagM_nsbtx:
    .asciiz "Player/get/gd_bcbagM.nsbtx"
    .fill 3, 0
random_treasure_nsbmd:
    .asciiz "Player/get/gd_sango.nsbmd"
    .fill 4, 0
random_treasure_nsbtx:
    .asciiz "Player/get/gd_sango.nsbtx"
    .fill 4, 0
