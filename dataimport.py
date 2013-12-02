import MySQLdb
import numpy as np
from collections import defaultdict
#from matplotlib.nxutils import points_inside_poly
import matplotlib.path as mplp
from scipy.io import loadmat
from os.path import join as pjoin

#import sys
#sys.path.append('/home/jan/workspace/FUimaging/')
import ImageAnalysisComponents as ia


HADDAD = [('THREEDMORSE', 'Mor04v'), ('TOPOLOGICAL', 'MAXDN'),
           ('THREEDMORSE', 'Mor32m'), ('ATOMCENTRED_FRAGMENTS', 'O-057'), ('ATOMCENTRED_FRAGMENTS', 'O-057'),
           ('GEOMETRICAL', 'AROM'), ('THREEDMORSE', 'Mor25m'), ('THREEDMORSE', 'Mor25m'),
           ('EIGENVALUE_INDICES', 'SEige'), ('ATOMCENTRED_FRAGMENTS', 'C-027'),
           ('GEOMETRICAL', 'DISPm'), ('THREEDMORSE', 'Mor08v'), ('THREEDMORSE', 'Mor08v'), ('THREEDMORSE', 'Mor08v'), ('GETAWAY', 'R1e+'),
           ('THREEDMORSE', 'Mor25e'), ('GETAWAY', 'HATS6m'),
           ('EDGE_ADJACENCY_INDICES', 'EEig11r'),
           ('BURDEN_EIGENVALUES_DESCRIPTORS', 'BELm8'), ('GEOMETRICAL', 'DISPe'),
           ('WHIM', 'P1s'), ('ATOMCENTRED_FRAGMENTS', 'C-040'), ('ATOMCENTRED_FRAGMENTS', 'C-040'),
           ('CONSTITUTIONAL', 'nBnz'), ('TWOD_AUTOCORRELATIONS', 'GATS1m'),
           ('TOPOLOGICAL_CHARGE_INDICES', 'JGT'), ('FUNCTIONAL_GROUP_COUNTS', 'nArOH'),
           ('EDGE_ADJACENCY_INDICES', 'EEig12x'), ('ATOMCENTRED_FRAGMENTS', 'N-075'),
           ('FUNCTIONAL_GROUP_COUNTS', 'nRCOOH'), ('FUNCTIONAL_GROUP_COUNTS', 'nRCOOH'),
           ('FUNCTIONAL_GROUP_COUNTS', 'nCp'), ('GETAWAY', 'R2p'), ('GETAWAY', 'R2p'), ('GETAWAY', 'R2p'),
           ('TOPOLOGICAL', 'Jhetm'), ('WHIM', 'G1m'), ('GEOMETRICAL', 'SPAM'),
           ('CONSTITUTIONAL', 'nDB'), ('GETAWAY', 'R2m+')]

SAITO = [('TOPOLOGICAL', 'TI2'), ('WALK_PATH_COUNTS', 'MPC04'),
         ('CONNECTIVITY_INDICES', 'X2v'), ('INFORMATION_INDICES', 'HVcpx'),
         ('TWOD_AUTOCORRELATIONS', 'GATS1m'), ('RDF', 'RDF110m'),
         ('WHIM', 'G2v'), ('GETAWAY', 'HATS2u'), ('GETAWAY', 'HATS0p'),
         ('GETAWAY', 'R4m+'), ('GETAWAY', 'R2e'), ('GETAWAY', 'R6p'),
         ('GETAWAY', 'R6p'), ('GETAWAY', 'RTp+'), ('ATOMCENTRED_FRAGMENTS', 'H-049'),
         ('ATOMCENTRED_FRAGMENTS', 'O-057'), ('MOLECULAR_PROPERTIES', 'Hy'), ('MOLECULAR_PROPERTIES', 'Hy'),
         ('MOLECULAR_PROPERTIES', 'TPSA(NO)') , ('MOLECULAR_PROPERTIES', 'TPSA(Tot)')]



class csvInterface(object):
    def __init__(self, location):
        self.location = location

    def make_tabledict(self, desc, table):
        print desc, table
        fname = self.location + table + '.csv'
        fh = open(fname)
        headers = fh.readline().strip('\r\n').split(',')
        fh.close()
        if desc == 'all':
            data = np.loadtxt(fname, delimiter=',', skiprows=1, usecols=range(2, len(headers)))
        else:
            col_ix = [headers.index(i) for i in desc]
            data = np.loadtxt(fname, delimiter=',', skiprows=1, usecols=col_ix)
        molids = np.loadtxt(fname, delimiter=',', skiprows=1, usecols=[0])
        identify = np.loadtxt(fname, dtype=str, delimiter=',', skiprows=1, usecols=[1])
        tabledict = {}
        for mol_ix, mol in enumerate(molids):
            if not 'error' in identify[mol_ix]:
                tabledict[int(mol)] = data[mol_ix]
                if data[mol_ix] == -999:
                    print int(mol), data[mol_ix]
        return tabledict

class instantJChemInterface(object):
    def __init__(self, where='localhost', who='jan', db='ODORDB'):
        self.conn = MySQLdb.connect(where, who, '', db)

    def get_descriptors(self, table, startrow=3):
        cursor = self.conn.cursor()
        cursor.execute("SHOW COLUMNS FROM " + table)
        out = cursor.fetchall()
        out = [i[0] for i in out][startrow:]
        cursor.close()
        return out

    def fetch_data(self, rows, table):
        ''' returns the data of rows in table'''
        rowstr = ('%s, ' * len(rows) % tuple(rows))[:-2]
        cursor = self.conn.cursor()
        cursor.execute("SELECT " + rowstr + " FROM " + table)
        out = cursor.fetchall()
        cursor.close()
        return out

    def fetch_selected_data(self, table, cols_out, col_select, val_select):
        ''' returns the columns which match val_select'''
        colstr = ('%s, ' * len(cols_out) % tuple(cols_out))[:-2]
        select = []
        seperator = ' AND '
        for ind, col in enumerate(col_select):
            val = val_select[ind] if len(col_select) == len(val_select) else val_select[0]
            select.append(col + '%s' % val)
        select = seperator.join(select)
        cursor = self.conn.cursor()
        #print 'SELECT %s FROM %s WHERE %s' % (colstr, table, select)
        cursor.execute('SELECT %s FROM %s WHERE %s'
                                % (colstr, table, select))
        out = cursor.fetchall()
        cursor.close()
        return out

    def make_tabledict(self, idkey, desc, table, col_select=['True'], val_select=[''], verbose=False):
        '''
        new version!!
        idkey (= dic key), property, table, [col_select], [val_select]
        '''
        tabledict = defaultdict(list)
        raw_data = self.fetch_selected_data(table, [idkey] + desc, col_select, val_select)
        for sample in raw_data:
            if verbose and (sample[0] in tabledict):
                print 'Warning DoubleKey: ', sample[0]
            tabledict[sample[0]] += sample[1:]
        return tabledict

    def make_table_dict(self, idkey, desc, table, col_select=['True'], val_select=['']):
        ''' 
        decepreated, use make_tabledict
        idkey (= dic key), property, table, [col_select], [val_select]
        '''
        print '!!!!!!!!!!!! decepreated, use make_tabledict !!!!!!!!!!!!!'
        tabledict = {}
        raw_data = self.fetch_selected_data(table, [idkey] + desc, col_select, val_select)
        for sample in raw_data:
            try:
                tabledict[sample[0]].append(list(sample[1:]))
            except KeyError:
                tabledict[sample[0]] = [list(sample[1:])]
        return tabledict

    def write_data(self, table_name, col_name, col_type, idcol, id_dict):
        cursor = self.conn.cursor()
        #cursor.execute('ALTER TABLE %s ADD %s %s' % (table_name, col_name, col_type))
        for (idkey, data) in id_dict.items():

            cursor.execute('SELECT %s FROM %s WHERE %s=%s' % (idcol, table_name, idcol, idkey))
            print 'SELECT %s FROM %s WHERE %s=%s' % (idcol, table_name, idcol, idkey)
            isthere = cursor.fetchall()
            print isthere
            if isthere:
                print 'yes'
            if isthere:
                print 'already there'
                sqlcommand = 'UPDATE %s SET %s="%' + '%s"' % col_type + ' WHERE %s=%s'
                #print sqlcommand % (table_name, col_name, data, idcol, idkey)
                #print data, sqlcommand % (table_name, col_name, data, idcol, idkey)
                cursor.execute(sqlcommand % (table_name, col_name, data, idcol, idkey))
            else:
                #print 'INSERT INTO %s (%s, %s) VALUES (%s, "%s")' % (table_name, idcol, col_name, idkey, data)
                sqlcommand = 'INSERT INTO %s (%s, %s) VALUES (%s, "%s")'
                #print sqlcommand % (table_name, idcol, col_name, idkey, data)
                cursor.execute(sqlcommand % (table_name, idcol, col_name, idkey, data))
        cursor.close()
        self.conn.commit()

    def update(self, table_name, col_name, col_type, idcol, id_dict):
        cursor = self.conn.cursor()
        #cursor.execute('ALTER TABLE %s ADD %s %s' % (table_name, col_name, col_type))
        for (idkey, data) in id_dict.items():
            sqlcommand = 'UPDATE %s SET %s="%' + '%s"' % col_type + ' WHERE %s=%s'
            cursor.execute(sqlcommand % (table_name, col_name, data, idcol, idkey))
        cursor.close()
        self.conn.commit()

    def filter_dict(self, response_dict, feature_dict):
        for key in response_dict.keys():
            if response_dict[key] == ['?']:
                response_dict.pop(key)
                feature_dict.pop(key)

class LoadRoi():

    """ ======== load in 2p selected ROIs ======== """

    def __init__(self, path, filename='nrois.mat', keys=('nxis', 'nyis'), uwidth=1024):
        self.path = path
        self.file = filename
        self.keys = keys
        self.uwidth = uwidth

    def __call__(self, shape):
        rois_vert = loadmat(pjoin(self.path, self.file))
        num_rois = rois_vert[self.keys[0]].shape[1]

        temp_grid = np.indices(shape)
        grid = np.array(zip(temp_grid[1].flatten(), temp_grid[0].flatten()))

        rois = []
        for roi_ind in range(num_rois):
            x_edge = rois_vert[self.keys[0]][:, roi_ind] / (self.uwidth / shape[0])
            y_edge = rois_vert[self.keys[1]][:, roi_ind] / (self.uwidth / shape[0])
            num_edges = np.sum(x_edge != 0)
            verts = np.array(zip(x_edge, y_edge))[:num_edges]
            path = mplp.Path(verts)
            points_in_poly = path.contains_points(grid)
            rois.append(points_in_poly)
        rois = np.array(rois)
        rois = ia.TimeSeries(rois, name=[self.path], typ='mask', shape=shape,
                          label_stimuli=['ROI' + str(i) for i in range(rois.shape[0])])
        return rois
