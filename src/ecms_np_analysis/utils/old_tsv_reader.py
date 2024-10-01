from collections import OrderedDict, defaultdict
import pandas as pd
import itertools

def parse_ec_ms_select_mass_csv(fpath: str, sep: str = '\t'):
    metadata = {}
    # data = OrderedDict()
    col_widths = OrderedDict()
    data_cols = []
    with open(fpath) as f:
        
        # parse initial header lines to get section lengths
        for _ in range(3):
            line = next(f)
            contents = line.rstrip().split(sep)
            metadata[contents[0]] = int(contents[-1])

        if int(metadata["num_data_header_lines"]) != 2:
            raise NotImplementedError("Cannot parse datafile with num data header lines not 2")
        
        # parse rest of header lines
        for _ in range(metadata["num_header_lines"] - 3):
            line = next(f)
            contents = line.rstrip().split(sep)

            if contents[2] == "":
                metadata[contents[0]] = contents[-1]
            elif contents[2] in metadata:
                metadata[contents[2]][contents[0]] = contents[-1]
            else:
                metadata[contents[2]] = {
                    contents[0]: contents[-1],
                }

        # parse data header lines and get column names and widths
        # for _ in range(int(metadata["num_data_header_lines"])):
        line = next(f)
        contents = line.rstrip().split(sep)
        col_name = contents[0]
        count=1
        for col in contents[1:]:
            if col == "":
                count += 1
            else:
                col_widths[col_name] = count
                count = 1
                col_name = col
        
        col_widths[col_name] = count

        
        prefixes = []
        for col_name, width in col_widths.items():
            prefixes += [ col_name for _ in range(width)]


        line = next(f)
        contents = line.rstrip().split(sep)

        # data_cols_single_line = []

        for i, col in enumerate(contents):
            data_cols.append(
                "{} {}".format(prefixes[i], col)
            )
    
    # import pdb; pdb.set_trace()

    data_df = pd.read_csv(
        fpath,
        sep='\t',
        skiprows=metadata["data_start"],
        names=data_cols,
        index_col=False,
    )



            
    return metadata, data_df
    

def main():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "tsv_file",
        type=str,
    )

    args = parser.parse_args()

    metadata, data = parse_ec_ms_select_mass_csv(args.tsv_file)

    print(data.head())

    #print(metadata)

    

if __name__ == "__main__":
    main()