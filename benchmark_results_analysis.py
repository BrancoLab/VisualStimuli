import matplotlib.pyplot as plt
import matplotlib
import datetime
import numpy as np
from nptdms import TdmsFile
from math import factorial

matplotlib.rc('axes',edgecolor=[0.8, 0.8, 0.8])
matplotlib.rcParams['text.color'] = [0.8, 0.8, 0.8]
matplotlib.rcParams['axes.labelcolor'] = [0.8, 0.8, 0.8]
matplotlib.rcParams['axes.labelcolor'] = [0.8, 0.8, 0.8]
matplotlib.rcParams['xtick.color'] = [0.8, 0.8, 0.8]
matplotlib.rcParams['ytick.color'] = [0.8, 0.8, 0.8]
params = {'legend.fontsize': 12,
          'legend.handlelength': 1}
plt.rcParams.update(params)

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def line_smoother(y, window_size, order, deriv=0, rate=1):
    # Apply a Savitzy-Golay filter to smooth traces
    order_range = range(order + 1)
    half_window = (window_size - 1) // 2
    # precompute coefficients
    b = np.mat([[k ** i for i in order_range] for k in range(-half_window, half_window + 1)])
    m = np.linalg.pinv(b).A[deriv] * rate ** deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    try:
        firstvals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])
        lastvals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
        y = np.concatenate((firstvals, y, lastvals))
        return np.convolve(m[::-1], y, mode='valid')
    except:
        y = np.array(y)
        firstvals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])
        lastvals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
        y = np.concatenate((firstvals, y, lastvals))
        return np.convolve(m[::-1], y, mode='valid')

def read_ldr_data():
    th = 4.99631

    filepath = '.\\Test Data\\Camera_LDR-default-6-89730178.tdms'

    t = TdmsFile(filepath)

    data = []
    for sweep in t.group_channels('AI0'):
        data.append(sweep.data)
    data = np.array([item for sublist in data for item in sublist])

    data = data[12000:]
    data[data<4.988] = 4.988
    real_data = data.copy()
    data = line_smoother(data, 1001, 5)

    high_points = data.copy()
    high_points[high_points<th] = 0
    high_points[high_points>0] = 1

    switches = -(high_points[0:-1] - high_points[1:])

    a, b = np.zeros(len(switches)), np.zeros(len(switches))
    a[np.where(switches>0)] = 1
    b[np.where(switches<0)] = 1

    f, ax = plt.subplots(1, 1, facecolor=[0.1, 0.1, 0.1])
    ax.set(ylim=[4.994, 5], facecolor=[0.2, 0.2, 0.2], xlim=[350000, 479500])
    ax.plot(real_data, alpha=0.735, color=[0.8, 0.4, 0.4], linewidth=0.25)

    ax.plot(data, alpha=0.75, color=[0.8, 0.8, 0.8], linewidth=3)

    ax.plot(np.multiply(a, 5), alpha=0.75, color=[0.2, 0.8, 0.2], linewidth=3)
    ax.plot(np.multiply(b, 5), alpha=0.75, color=[0.2, 0.3, 0.7], linewidth=3)


    plt.show()

    ups = np.where(switches>0)[0]
    downs = np.where(switches<0)[0]
    print(len(ups), len(downs))
    intervals = []
    for off in downs:
        closest = find_nearest(ups[ups<off], off)
        intervals.append(off-closest+1)

    avg_length = np.mean(intervals)/2500
    std_length = np.std(intervals)

    a = 1


def plot_benchmark_results(results):
    # read_ldr_data()


    f, axarr = plt.subplots(3, 1, facecolor=[0.1, 0.1, 0.1])
    f.tight_layout()
    for idx, ax in enumerate(axarr):
        ax.set(facecolor=[0.2, 0.2, 0.2])

    axarr[0].set(title='Stim duration (ms)')
    axarr[0].plot([x*1000 for x in results['Stim duration']], color='red', label='Stim duration')
    axarr[0].plot([x*results['Ms per frame'] for x in results['Number frames per stim']],
                  color=[0.75, 0.75, 0.75], label='Calculated duration')



    results['Draw duration all'] = np.multiply(results['Draw duration all'], 1000)
    colors = np.linspace(0, 1, len(results['Draw duration all'][0]))
    axarr[1].set(title='Frame draw duration individual frames (ms)', ylim=[0, np.max(results['Draw duration all'])+5])
    xx = [np.ones(len(x))*idx for idx,x in enumerate(results['Draw duration all'])]
    for num in range(len(xx)):
        axarr[1].scatter(xx[num], results['Draw duration all'][num], s=14, c=np.array(colors)[::-1], cmap='gray')
    axarr[1].axhline(results['Ms per frame'], color=[.6, .6, .6], label='Ms per frame')


    axarr[2].set(title='Frame draw duration avg and std per stimulus (ms)', ylim=[0, 40])
    axarr[2].plot(np.multiply(results['Draw duration avg'], 1000), color='green', linewidth=5,
                  label='Draw duration avg')
    axarr[2].plot(np.multiply(results['Draw duration std'], 1000), color=[0.8, 0.5, 0.5], linewidth=5,
                  label='Draw duration std')
    axarr[2].plot(results['Number dropped frames'], color='red', linewidth=3, label='Dropped')
    axarr[2].axhline(results['Ms per frame'], color=[.6, .6, .6], label='Ms per frame')


    for ax in axarr:
        legend = ax.legend(frameon=True)
        frame = legend.get_frame()
        frame.set_facecolor([0.1, 0.1, 0.1])

    # Save results in case something crashes
    timestamp = datetime.datetime.today().strftime('%d%b%Y_%H%M')
    name = results['Stim name'].split('.')[0]+'_'+results['Monitor name']+'_'+timestamp
    f.savefig(".\\Tests Results\\{}.png".format(name))

    plt.figure()
    for i in range(len(results['Draw duration all'])):
        plt.plot(results['Draw duration all'][i])

    plt.show()


    a = 1




if __name__=="__main__":
    read_ldr_data()

