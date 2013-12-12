import matplotlib
import matplotlib.pyplot as plt
import numpy as np

class AssignMode(object):

    def __init__(self, data_dict):
        """ data_dict should contain factorization mf, bg-image bg and  listdict alias"""

        #create layout
        self.fig = plt.figure(figsize=(20, 10))
        gs = matplotlib.gridspec.GridSpec(1, 2)
        self.ax_contour = self.fig.add_subplot(gs[0])
        self.ax_base = self.fig.add_subplot(gs[1])
        ax_button = self.fig.add_axes([0.75, 0.9, 0.1, 0.075])
        self.button = matplotlib.widgets.Button(ax_button, 'MOR18-2')

        # connect callbacks
        self.fig.canvas.mpl_connect('button_press_event', self._show_base)
        self.button.on_clicked(self._store_alias)

        # read in data
        self.bg = data_dict['bg']
        self.mf = data_dict['mf']
        self.alias = data_dict['alias']
        self.mode_map = np.argmax(self.mf.base.shaped2D(), 0)

        # draw intial
        self.myextent = np.array([0, self.mf.base.shape[1], self.mf.base.shape[0], 0]) - 0.5
        self.ax_base.imshow(self.bg, extent=self.myextent, cmap=plt.cm.bone)
        self._base_overview()
        self.drawn_mode = None
        self.fig.suptitle(self.mf.name)

    def _base_overview(self):
        self.ax_contour.clear()
        self.ax_contour.imshow(self.bg, extent=self.myextent, cmap=plt.cm.bone)
        for m_ix, m in enumerate(self.mf.base.shaped2D()):
            colormap = ['c', 'b'] if (self.mf.t2t[m_ix] < 0.5) else ['w', '0.5']
            if ('MOR18-2' in self.alias) and  (m_ix in self.alias['MOR18-2']):
                colormap = [[1, 1, 0], 'r']
            alpha = 0.5 if (self.mf.t2t[m_ix] < 0.5) else 0.2
            self.ax_contour.contourf(m, [0.5, 0.7, 1], colors=colormap, alpha=alpha)


    def _show_base(self, event):
        if event.inaxes in [self.ax_base, self.ax_contour]:
            self.current_mode = self.mode_map[int(round(event.ydata)), int(round(event.xdata))]
            if self.drawn_mode:
                [i.remove() for i in self.drawn_mode.collections]
            im = self.mf.base.shaped2D()[self.current_mode]
            self.drawn_mode = self.ax_base.contour(im, [-0.5, 0, 0.25, 0.5, 0.75], colors=['m', 'b', 'c', 'g', 'r'])
            plt.draw()

    def _store_alias(self, event):
        if 'MOR18-2' not in self.alias:
            self.alias['MOR18-2'] = []
        if self.current_mode in self.alias['MOR18-2']:
            self.alias['MOR18-2'].remove(self.current_mode)
        else:
            self.alias['MOR18-2'].append(self.current_mode)
        self._base_overview()
        plt.draw()
