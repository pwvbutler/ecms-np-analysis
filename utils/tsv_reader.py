from collections import OrderedDict, defaultdict
import pandas as pd
import itertools


def parse_metadata_header_from_fpath(fpath: str, sep: str = '\t'):
    """
    parse tsv metadata header lines using filepath of tsv file

    Args:
        fpath (str): path to tsv file
        sep (str): separator character for file, default '\t'

    Returns:
        metadata (dict): the metadata parsed with fields as keys
            and the corresponding data as values  
    """
    with open(fpath) as f:
        metadata = parse_metadata_header(f, sep=sep)
    
    return metadata
    

def parse_metadata_header(file_obj, sep: str = '\t'):
    """
    parse tsv metadata header lines using file handler object

    Args:
        file_obj: open file object
        sep (str): separator character for file, default '\t'

    Returns:
        metadata (dict): the metadata parsed with fields as keys
            and the corresponding data as values  
    """
    metadata = {}

    # parse initial header lines to get section lengths
    for _ in range(3):
        try:
            line = next(file_obj)
            contents = line.rstrip().split(sep)
            metadata[contents[0]] = int(contents[-1])
        except Exception as e:
            raise ValueError("unable to parse initial lines of tsv file: {}".format(e))
    
    # parse rest of header lines
    for _ in range(metadata["num_header_lines"] - 3):
        line = next(file_obj)
        contents = line.rstrip().split(sep)

        if contents[2] == "":
            metadata[contents[0]] = contents[-1]
        elif contents[2] in metadata:
            metadata[contents[2]][contents[0]] = contents[-1]
        else:
            metadata[contents[2]] = {
                contents[0]: contents[-1],
            }

    return metadata


def parse_data_header_from_fpath(fpath: str, num_metadata_lines: int, num_data_header_lines: int, sep: str = '\t'):
    """
    parse tsv data header lines using filepath of tsv file

    Args:
        fpath (str): path to tsv file
        num_metadata_lines (int): number of metadata header lines
        num_data_header_lines (int): number of data header lines to parse
        sep (str): separator character for file, default '\t'

    Returns:
        col_names (list[str]): Single line names for each column in data section 
    """
    with open(fpath) as f:
        col_names = parse_data_header(f, num_metadata_lines, num_data_header_lines, sep=sep)

    return col_names


def parse_data_header(file_obj, num_metadata_lines: int, num_data_header_lines: int, sep: str = '\t'):
    """
    parse tsv data header lines using file handler object

    Args:
        fpath (str): path to tsv file
        num_metadata_lines (int): number of metadata header lines
        num_data_header_lines (int): number of data header lines to parse
        sep (str): separator character for file, default '\t'

    Returns:
        col_names (list[str]): Single line names for each column in data section 
    """

    if int(num_data_header_lines) != 2:
        raise NotImplementedError("Cannot parse datafile with num data header lines not 2")

    col_widths = OrderedDict()
    col_names = []
    start_line = num_metadata_lines
    end_line = num_metadata_lines + num_data_header_lines

    file_iter = itertools.islice(
        file_obj, start_line, end_line,
    )

    # parse data header first line and get base column names and widths
    line = next(file_iter)
    contents = line.rstrip().split(sep)
    col_name = contents[0]
    count=1
    for col in contents[1:]:
        if col == "": # if empty, assume continuing column name
            count += 1
        else:
            col_widths[col_name] = count
            count = 1
            col_name = col
    
    col_widths[col_name] = count
    
    # use widths to create a single row for column names
    for col_name, width in col_widths.items():
        col_names += [ col_name for _ in range(width)]

    # parse second line of data header and add contents to corresponding base column names
    line = next(file_iter)
    contents = line.rstrip().split(sep)

    # make sure base column names covers the final columns
    if len(contents) > len(col_names):
        col_names += [ col_names[-1] for _ in range(len(contents) - len(col_names))]

    for i, content in enumerate(contents):
        # col_names.append(
        #     "{} {}".format(col_names[i], col)
        # )

        col_names[i] = "{} {}".format(col_names[i], content)
    
    return col_names

def parse_tsv_data(f, data_start_line: int, col_names: list[str], sep: str = '\t'):
    """
    Read the tsv data

    Args:
        f (str, IOString, FileHandler): the tsv file reference
        data_start_line (int): the line number where the data starts
        col_names: the names of the columns for the data
        separator character for file, default '\t'
    """
    return pd.read_csv(
        f,
        sep=sep,
        skiprows=data_start_line,
        names=col_names,
        index_col=False,
    )

