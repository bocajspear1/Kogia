import pefile
from elftools.elf.elffile import ELFFile
from elftools.common.exceptions import ELFError
from elftools.elf.sections import SymbolTableSection
from elftools.elf.dynamic import DynamicSection, DynamicSegment
from elftools.elf.gnuversions import (
    GNUVerSymSection, GNUVerDefSection,
    GNUVerNeedSection,
    )
import sys 



def parse_pe(file_path):
    try:
        pe = pefile.PE(file_path)
        if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
            for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                name = exp.name.decode('utf8')
                if name is None or name == "":
                    name = f"#{exp.ordinal}"
                print(
                    "EXPORT", name, hex(pe.OPTIONAL_HEADER.ImageBase + exp.address), exp.ordinal
                )
        for imp_lib in pe.DIRECTORY_ENTRY_IMPORT:
            lib = imp_lib.dll.decode('utf8').lower()
            print("IMPORT_LIB", lib)

            for imp in imp_lib.imports:
                name = imp.name.decode('utf8')
                if name is None or name == b"":
                    name = f"#{imp.ordinal}"
                print("IMPORT", name + "@" + lib)
        return True
    except pefile.PEFormatError:
        return False


def parse_elf(file_path):
    try:
        with open(file_path, 'rb') as file:
            elffile = ELFFile(file)

            version_symbols = None
            version_defitions = None
            version_needs = None

            lib_map = {}

            for section in elffile.iter_sections():
                if not isinstance(section, DynamicSection):
                    continue
                for tag in section.iter_tags():
                    if tag.entry.d_tag == 'DT_NEEDED':
                        lib_map[tag.needed] = ""
                        print("IMPORT_LIB", tag.needed)

            for section in elffile.iter_sections():
                if isinstance(section, GNUVerSymSection):
                    version_symbols = section 
                if isinstance(section, GNUVerDefSection):
                    version_defitions = section 
                if isinstance(section, GNUVerNeedSection):
                    version_needs = section 
            
            for section in elffile.iter_sections():
                if not isinstance(section, SymbolTableSection):
                    continue
                for nsym, symbol in enumerate(section.iter_symbols()):
                    symbol_name = symbol.name
                    symbol_lib = ""
                    
                    if version_symbols:
                        symbol = version_symbols.get_symbol(nsym)
                        index = symbol.entry['ndx']
                        if not index in ('VER_NDX_LOCAL', 'VER_NDX_GLOBAL'):
                            index = int(index)
                            if version_defitions:
                                _, verdaux_iter = version_defitions.get_version(index)
                                symbol_lib = next(verdaux_iter).name
                            elif version_needs:
                                verneed, vernaux = version_needs.get_version(index)
                                symbol_lib = verneed.name
                    if symbol_name != "" and symbol_lib != "":
                        print("IMPORT", symbol_name + "@" + symbol_lib)

        return True
    except ELFError:
        return False



def main():
    file_path = sys.argv[1]
    ok = parse_pe(file_path)
    if not ok:
        parse_elf(file_path)


main()
            