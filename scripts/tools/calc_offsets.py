import re

sizes = {
    'Int32': 4, 'Single': 4, 'Double': 8, 'byte': 1, 'Int16': 2, 'Int8': 1,
    'Float32': 4, 'Float64': 8, 'UInt32': 4, 'UInt16': 2, 'UInt8': 1,
    'Int64': 8, 'UInt64': 8, 'Boolean': 1, 'Byte': 1, 'SByte': 1, 'Char': 2,
    'String': 4, 'Void': 0, 'sbyte': 1, 'char': 2, 'string': 4, 'void': 0
}

structs = {}

with open('data.cs', 'r') as f:
    lines = f.readlines()

current_struct = None
for line in lines:
    line = line.strip()
    if line.startswith('internal struct'):
        current_struct = line.split()[2].split('<')[0]
        structs[current_struct] = []
    elif line.startswith('public') and current_struct:
        parts = line.split()
        type_name = parts[1]
        var_name = parts[2].split(';')[0]
        
        array_size = 1
        if '[MarshalAs(UnmanagedType.ByValArray, SizeConst =' in lines[lines.index(line+'\n')-1 if line+'\n' in lines else 0]:
            pass # Need a better way to handle arrays
            
        structs[current_struct].append((type_name, var_name))

def get_size(type_name):
    if type_name in sizes:
        return sizes[type_name]
    if type_name.startswith('Vector3'):
        return get_size(type_name.split('<')[1].split('>')[0]) * 3
    if type_name.startswith('Orientation'):
        return get_size(type_name.split('<')[1].split('>')[0]) * 3
    if type_name.startswith('TireData'):
        return get_size(type_name.split('<')[1].split('>')[0]) * 4
    if type_name.startswith('Sectors'):
        return get_size(type_name.split('<')[1].split('>')[0]) * 3
    if type_name.startswith('RaceDuration'):
        return get_size(type_name.split('<')[1].split('>')[0]) * 3
    if type_name.startswith('SectorStarts'):
        return get_size(type_name.split('<')[1].split('>')[0]) * 3
    if type_name == 'DriverInfo':
        return 64 + 4*12
    if type_name == 'CutTrackPenalties':
        return 4*5
    if type_name == 'Flags':
        return 4*3 + 4 + 4*5
    if type_name == 'CarDamage':
        return 4*6
    if type_name == 'PitMenuState':
        return 4*11
    if type_name == 'TireTempInformation':
        return 4*3 + 4*3
    if type_name == 'BrakeTemp':
        return 4*4
    if type_name == 'AidSettings':
        return 4*5
    if type_name == 'DRS':
        return 4*4
    if type_name == 'PushToPass':
        return 4*4 + 4*2
    if type_name == 'PlayerData':
        return 4 + 8 + 8*3*11 + 8*9 + 8*4*4 + 8*7
    if type_name == 'DriverData':
        return get_size('DriverInfo') + 4*4 + 4 + 4*3 + 4*3 + 4 + 4*3 + 4*3 + 4*3 + 4*2 + 4*2 + 4 + get_size('CutTrackPenalties') + 4 + 4*4 + 4*2 + 4*2 + 4*4
    return 0

# Let's just use the r3e-api package to get the offsets!
