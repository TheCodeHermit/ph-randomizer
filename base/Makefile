.PHONY: all debug

# Set ARM compiler
CC=arm-none-eabi-gcc

# Set up compilation flags
CFLAGS	:=	-marm -mno-thumb-interwork -march=armv5te -mtune=arm946e-s -fno-inline -Wall -Os

# C source file directory
SRC_DIR=code
SRC=$(wildcard $(SRC_DIR)/*.c)
OBJ=$(SRC:.c=.o)
ASM=$(SRC:.c=.asm)

INPUT_NDS_FILE=$(PH_ROM_PATH)
PREPATCHED_NDS_FILE=prepatched.nds
OUTPUT_NDS_FILE=out.nds
OUTPUT_BPS_FILE=patch.bps

# Set version string to a default if it isn't provided
VERSION_STRING := $(or $(VERSION_STRING), "no_version")

$(OUTPUT_BPS_FILE): $(INPUT_NDS_FILE) $(OUTPUT_NDS_FILE)
	./flips --create $^ $@

$(OUTPUT_NDS_FILE): $(PREPATCHED_NDS_FILE) $(OBJ)
	python3 extract_rom.py $(PREPATCHED_NDS_FILE) .
	./armips code/main.asm

	python3 rebuild_rom.py $(PREPATCHED_NDS_FILE) overlay/ arm9_header.bin arm9_compressed.bin $(OUTPUT_NDS_FILE)

$(PREPATCHED_NDS_FILE): $(INPUT_NDS_FILE)
	VERSION_STRING=$(VERSION_STRING) python3 data_patcher.py --input-rom $(INPUT_NDS_FILE) --output-rom $(PREPATCHED_NDS_FILE)

# Same as `all`, but also includes readable .asm file
debug: $(OBJ) $(ASM)

# Compile C source file to assembly code
%.asm: %.c
	$(CC) $(CFLAGS) -S "$<" -o "$@" -fverbose-asm

# Compile C source file to object file
%.o: %.c
	$(CC) $(CFLAGS) -c "$<" -o "$@"

all: $(OUTPUT_BPS_FILE)
