#!/usr/bin/env python3

# SPDX-FileCopyrightText: © 2022 Decompollaborate
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import enum


@enum.unique
class InputEndian(enum.Enum):
    BIG = enum.auto()
    LITTLE = enum.auto()
    MIDDLE = enum.auto()

compilerOptions = {"IDO", "GCC", "SN64"}

@enum.unique
class Compiler(enum.Enum):
    UNKNOWN = None
    IDO = "IDO"
    GCC = "GCC"
    SN64 = "SN64"

    @staticmethod
    def fromStr(value: str) -> Compiler:
        if value not in compilerOptions:
            return Compiler.UNKNOWN
        return Compiler(value)


class GlobalConfig:
    DISASSEMBLE_UNKNOWN_INSTRUCTIONS: bool = False
    """Try to disassemble non implemented instructions and functions"""

    ADD_NEW_SYMBOLS: bool = True
    PRODUCE_SYMBOLS_PLUS_OFFSET: bool = True
    TRUST_USER_FUNCTIONS: bool = True
    TRUST_JAL_FUNCTIONS: bool = True

    STRING_GUESSER: bool = True
    """Rodata string guesser"""

    AUTOGENERATED_NAMES_BASED_ON_SECTION_TYPE: bool = True
    """Name autogenerated symbols after the section those are come from

    Use R_ for symbols in .rodata and B_ for symbols in .bss"""

    AUTOGENERATED_NAMES_BASED_ON_DATA_TYPE: bool = True
    """Name autogenerated symbols after their type

    Use STR_ for strings, FLT_ for floats and DBL_ for doubles"""

    COMPILER: Compiler = Compiler.IDO

    ENDIAN: InputEndian = InputEndian.BIG
    """Endian for input binary files"""

    GP_VALUE: int|None = None
    """Value used for $gp relocation loads and stores"""

    SYMBOL_FINDER_FILTER_LOW_ADDRESSES: bool = True
    """Toggle pointer detection for lower addresses (lower than 0x40000000)"""
    SYMBOL_FINDER_FILTER_HIGH_ADDRESSES: bool = True
    """Toggle pointer detection for higher addresses (higher than 0xC0000000)"""
    SYMBOL_FINDER_FILTERED_ADDRESSES_AS_CONSTANTS: bool = True
    """Treat filtered out addresses as constants pairs"""
    SYMBOL_FINDER_FILTERED_ADDRESSES_AS_HILO: bool = True
    """Allow using %hi/%lo syntax for filtered out addresses"""


    ASM_COMMENT: bool = True
    """Toggle the comments in generated assembly code"""
    GLABEL_ASM_COUNT: bool = True
    """Toggle the glabel count comment on functions"""

    ASM_TEXT_LABEL: str = "glabel"
    ASM_DATA_LABEL: str = "glabel"
    ASM_TEXT_ENT_LABEL: str = ""
    ASM_TEXT_END_LABEL: str = ""
    ASM_TEXT_FUNC_AS_LABEL: bool = False

    PRINT_NEW_FILE_BOUNDARIES: bool = False
    """Print to stdout every file boundary found in .text and .rodata"""

    USE_DOT_BYTE: bool = True
    """Disassemble symbols marked as bytes with .byte instead of .word"""
    USE_DOT_SHORT: bool = True
    """Disassemble symbols marked as shorts with .short instead of .word"""

    LINE_ENDS: str = "\n"


    QUIET: bool = False
    VERBOSE: bool = False


    PRINT_FUNCTION_ANALYSIS_DEBUG_INFO: bool = False
    PRINT_SYMBOL_FINDER_DEBUG_INFO: bool = False
    PRINT_UNPAIRED_LUIS_DEBUG_INFO: bool = False


    REMOVE_POINTERS: bool = False
    IGNORE_BRANCHES: bool = False
    """Ignores the address of every branch, jump and jal"""
    IGNORE_WORD_LIST: set[int] = set()
    """Ignores words that starts in 0xXX"""
    WRITE_BINARY: bool = False
    """write to files splitted binaries"""


    @staticmethod
    def addParametersToArgParse(parser: argparse.ArgumentParser):
        backendConfig = parser.add_argument_group("Disassembler backend configuration")

        backendConfig.add_argument("--disasm-unknown", help=f"Force disassembling functions with unknown instructions. Defaults to {GlobalConfig.DISASSEMBLE_UNKNOWN_INSTRUCTIONS}", action=argparse.BooleanOptionalAction)

        backendConfig.add_argument("--string-guesser", help=f"Toggles the string guesser feature. Defaults to {GlobalConfig.STRING_GUESSER}", action=argparse.BooleanOptionalAction)

        backendConfig.add_argument("--name-vars-by-section", help=f"Toggles the naming-after-section feature for autogenerated names. This means autogenerated symbols get a R_ or B_ prefix if the symbol is from a rodata or bss section. Defaults to {GlobalConfig.AUTOGENERATED_NAMES_BASED_ON_SECTION_TYPE}", action=argparse.BooleanOptionalAction)
        backendConfig.add_argument("--name-vars-by-type", help=f"Toggles the naming-after-type feature for autogenerated names. This means autogenerated symbols can get a STR_, FLT_ or DBL_ prefix if the symbol is a string, float or double. Defaults to {GlobalConfig.AUTOGENERATED_NAMES_BASED_ON_DATA_TYPE}", action=argparse.BooleanOptionalAction)

        backendConfig.add_argument("--compiler", help=f"Enables some tweaks for the selected compiler. Defaults to {GlobalConfig.COMPILER.name}", choices=compilerOptions)

        backendConfig.add_argument("--endian", help=f"Set the endianness of input files. Defaults to {GlobalConfig.ENDIAN.name.lower()}", choices=["big", "little", "middle"], default=GlobalConfig.ENDIAN.name.lower())

        backendConfig.add_argument("--gp", help="Set the value used for loads and stores related to the $gp register. A hex value is expected")

        backendConfig.add_argument("--filter-low-addresses", help=f"Filter out low addresses (lower than 0x40000000) when searching for pointers. Defaults to {GlobalConfig.SYMBOL_FINDER_FILTER_LOW_ADDRESSES}", action=argparse.BooleanOptionalAction)
        backendConfig.add_argument("--filter-high-addresses", help=f"Filter out high addresses (higher than 0xC0000000) when searching for pointers. Defaults to {GlobalConfig.SYMBOL_FINDER_FILTER_HIGH_ADDRESSES}", action=argparse.BooleanOptionalAction)
        backendConfig.add_argument("--filtered-addresses-as-constants", help=f"Treat filtered out addressed as constants. Defaults to {GlobalConfig.SYMBOL_FINDER_FILTERED_ADDRESSES_AS_CONSTANTS}", action=argparse.BooleanOptionalAction)
        backendConfig.add_argument("--filtered-addresses-as-hilo", help=f"Use %hi/%lo syntax for filtered out addresses. Defaults to {GlobalConfig.SYMBOL_FINDER_FILTERED_ADDRESSES_AS_HILO}", action=argparse.BooleanOptionalAction)


        miscConfig = parser.add_argument_group("Disassembler misc options")

        miscConfig.add_argument("--asm-comments", help=f"Toggle the comments in generated assembly code. Defaults to {GlobalConfig.ASM_COMMENT}", action=argparse.BooleanOptionalAction)
        miscConfig.add_argument("--glabel-count", help=f"Toggle glabel count comment. Defaults to {GlobalConfig.GLABEL_ASM_COUNT}", action=argparse.BooleanOptionalAction)

        miscConfig.add_argument("--asm-text-label", help=f"Changes the label used to declare functions. Defaults to {GlobalConfig.ASM_TEXT_LABEL}")
        miscConfig.add_argument("--asm-data-label", help=f"Changes the label used to declare data symbols. Defaults to {GlobalConfig.ASM_DATA_LABEL}")
        miscConfig.add_argument("--asm-ent-label", help=f"Tells the disassembler to start using an ent label for functions")
        miscConfig.add_argument("--asm-end-label", help=f"Tells the disassembler to start using an end label for functions")
        miscConfig.add_argument("--asm-func-as-label", help=f"Toggle adding the function name as an additional label. Defaults to {GlobalConfig.ASM_TEXT_FUNC_AS_LABEL}", action=argparse.BooleanOptionalAction)

        miscConfig.add_argument("--print-new-file-boundaries", help=f"Print to stdout any new file boundary found. Defaults to {GlobalConfig.PRINT_NEW_FILE_BOUNDARIES}", action=argparse.BooleanOptionalAction)

        miscConfig.add_argument("--use-dot-byte", help=f"Disassemble symbols marked as bytes with .byte instead of .word. Defaults to {GlobalConfig.USE_DOT_BYTE}", action=argparse.BooleanOptionalAction)
        miscConfig.add_argument("--use-dot-short", help=f"Disassemble symbols marked as shorts with .short instead of .word. Defaults to {GlobalConfig.USE_DOT_SHORT}", action=argparse.BooleanOptionalAction)


        verbosityConfig = parser.add_argument_group("Verbosity options")

        verbosityConfig.add_argument("-V", "--verbose", help="Enable verbose mode", action=argparse.BooleanOptionalAction)
        verbosityConfig.add_argument("-q", "--quiet", help="Silence most of the output", action=argparse.BooleanOptionalAction)


        debugging = parser.add_argument_group("Disassembler debugging options")

        debugging.add_argument("--debug-func-analysis", help="Enables some debug info printing related to the function analysis)", action=argparse.BooleanOptionalAction)
        debugging.add_argument("--debug-symbol-finder", help="Enables some debug info printing related to the symbol finder system)", action=argparse.BooleanOptionalAction)
        debugging.add_argument("--debug-unpaired-luis", help="Enables some debug info printing related to the unpaired LUI instructions)", action=argparse.BooleanOptionalAction)


    @classmethod
    def parseArgs(cls, args: argparse.Namespace):
        if args.disasm_unknown is not None:
            GlobalConfig.DISASSEMBLE_UNKNOWN_INSTRUCTIONS = args.disasm_unknown

        if args.string_guesser is not None:
            GlobalConfig.STRING_GUESSER = args.string_guesser

        if args.name_vars_by_section is not None:
            GlobalConfig.AUTOGENERATED_NAMES_BASED_ON_SECTION_TYPE = args.name_vars_by_section
        if args.name_vars_by_type is not None:
            GlobalConfig.AUTOGENERATED_NAMES_BASED_ON_DATA_TYPE = args.name_vars_by_type

        if args.compiler is not None:
            GlobalConfig.COMPILER = Compiler.fromStr(args.compiler)

        if args.endian == "little":
            GlobalConfig.ENDIAN = InputEndian.LITTLE
        elif args.endian == "middle":
            GlobalConfig.ENDIAN = InputEndian.MIDDLE
        else:
            GlobalConfig.ENDIAN = InputEndian.BIG

        if args.gp is not None:
            GlobalConfig.GP_VALUE = int(args.gp, 16)

        if args.filter_low_addresses is not None:
            GlobalConfig.SYMBOL_FINDER_FILTER_LOW_ADDRESSES = args.filter_low_addresses
        if args.filter_high_addresses is not None:
            GlobalConfig.SYMBOL_FINDER_FILTER_HIGH_ADDRESSES = args.filter_high_addresses
        if args.filtered_addresses_as_constants is not None:
            GlobalConfig.SYMBOL_FINDER_FILTERED_ADDRESSES_AS_CONSTANTS = args.filtered_addresses_as_constants
        if args.filtered_addresses_as_hilo is not None:
            GlobalConfig.SYMBOL_FINDER_FILTERED_ADDRESSES_AS_HILO = args.filtered_addresses_as_hilo


        if args.asm_comments is not None:
            GlobalConfig.ASM_COMMENT = args.asm_comments
        if args.glabel_count is not None:
            GlobalConfig.GLABEL_ASM_COUNT = args.glabel_count

        if args.asm_text_label:
            GlobalConfig.ASM_TEXT_LABEL = args.asm_text_label
        if args.asm_data_label:
            GlobalConfig.ASM_DATA_LABEL = args.asm_data_label
        if args.asm_ent_label:
            GlobalConfig.ASM_TEXT_ENT_LABEL = args.asm_ent_label
        if args.asm_end_label:
            GlobalConfig.ASM_TEXT_END_LABEL = args.asm_end_label
        if args.asm_func_as_label is not None:
            GlobalConfig.ASM_TEXT_FUNC_AS_LABEL = args.asm_func_as_label

        if args.print_new_file_boundaries is not None:
            GlobalConfig.PRINT_NEW_FILE_BOUNDARIES = args.print_new_file_boundaries

        if args.use_dot_byte is not None:
            GlobalConfig.USE_DOT_BYTE = args.use_dot_byte
        if args.use_dot_short is not None:
            GlobalConfig.USE_DOT_SHORT = args.use_dot_short


        if args.verbose is not None:
            GlobalConfig.VERBOSE = args.verbose
        if args.quiet is not None:
            GlobalConfig.QUIET = args.quiet


        if args.debug_func_analysis is not None:
            GlobalConfig.PRINT_FUNCTION_ANALYSIS_DEBUG_INFO = args.debug_func_analysis
        if args.debug_symbol_finder is not None:
            GlobalConfig.PRINT_SYMBOL_FINDER_DEBUG_INFO = args.debug_symbol_finder
        if args.debug_unpaired_luis is not None:
            GlobalConfig.PRINT_UNPAIRED_LUIS_DEBUG_INFO = args.debug_unpaired_luis
