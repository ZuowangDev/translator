import gdspy


"""
path_of_map: input layermap
path_of_order_map: output layermap
path_of_csv: input translayer csv
input_gds: input GDSII
output_gds: output GDSII
"""

path_of_map = './cmos22fdsoi_tech.layermap'
path_of_order_map = './hlmc28FDSOI.layermap'
path_of_csv = './trans.csv'
input_gds = './28FDSOI_BL_22_PAD.gds'
output_gds = './PAD.gds'


# process value csv
def process_value_csv(str):
    translayer_dict = {}
    with open(str, 'r') as csvfile:
        reader = csvfile.readlines()
        # read the csv file through reading lines
        i = 0
        for row in reader:
            item = row.rstrip('\n').split(',')
            translayer_dict[(int(item[0]), int(item[1]))] = (int(item[2]), int(item[3])) if (item[2] != '' and item[3] != '') else ('', '')
            print(f"process row {i}")
            i += 1
    return translayer_dict

def replace_value(num_pairs, transvalue_dict):
    if (int(num_pairs[0]), int(num_pairs[1])) in transvalue_dict:
        return transvalue_dict[(int(num_pairs[0]), int(num_pairs[1]))]
    else:
        return ('', '')

# input: path of input and output GDSII, csv data in dict; output: new GDSII file
def process_gds(transvalue_dict: dict, path_of_input: str, path_of_output: str):
    untreated = []
    gdsii = gdspy.GdsLibrary()
    gdsii.read_gds(path_of_input)
    cell_dict = gdsii.cells
    
    for cell in cell_dict:
        print(cell)
        i = 0
        for polygon in cell_dict[cell].polygons:
            i += 1
            if i % 100 == 0:
                print(i)
            temp = replace_value((polygon.layers[0], polygon.datatypes[0]), transvalue_dict)
            if temp[0] != '' and temp[1] != '':
                polygon.layers = [temp[0]]
                polygon.datatypes = [temp[1]]
            else:
                cell_dict[cell].remove_polygons(lambda pts, layer, datatype: layer == polygon.layers[0] and datatype == polygon.datatypes[0])
                untreated.append((polygon.layers[0], polygon.datatypes[0]))
        for label in cell_dict[cell].labels:
            temp = replace_value((label.layer, label.texttype), transvalue_dict)
            if temp[0] != '' and temp[1] != '':
                label.layer = temp[0]
                label.texttype = temp[1]
            else:
                cell_dict[cell].remove_labels(lambda lbl: lbl == label)
                untreated.append((label.layer, label.texttype))
        for path in cell_dict[cell].paths:
            temp = replace_value((path.layers[0], path.datatypes[0]), transvalue_dict)
            if temp[0] != '' and temp[1] != '':
                path.layers = [temp[0]]
                path.datatypes = [temp[1]]
            else:
                cell_dict[cell].remove_paths(path)
                untreated.append((path.layers[0], path.datatypes[0]))
    gdsii.write_gds(path_of_output)

    print(f'Converted GDS file saved to: {path_of_output}')
    return untreated

def transform(path_of_map, path_of_csv, path_of_order_map, input_gds, output_gds):
    value_dict = process_value_csv(path_of_csv)
    list_w = process_gds(value_dict, input_gds, output_gds)
    with open('./IN22FDX_S1D_NFRG_W01024B032M04C128.log', 'w') as file:
    # create log file
        for item in list_w:
            # write the unset layer into log file
            file.write(f'{item}\n')

if __name__ == '__main__':
    transform(path_of_map, path_of_csv, path_of_order_map, input_gds, output_gds)
