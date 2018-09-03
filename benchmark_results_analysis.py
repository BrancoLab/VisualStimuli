import matplotlib.pyplot as plt
import matplotlib

matplotlib.rc('axes',edgecolor=[0.8, 0.8, 0.8])
matplotlib.rcParams['text.color'] = [0.8, 0.8, 0.8]
matplotlib.rcParams['axes.labelcolor'] = [0.8, 0.8, 0.8]
matplotlib.rcParams['axes.labelcolor'] = [0.8, 0.8, 0.8]
matplotlib.rcParams['xtick.color'] = [0.8, 0.8, 0.8]
matplotlib.rcParams['ytick.color'] = [0.8, 0.8, 0.8]
params = {'legend.fontsize': 12,
          'legend.handlelength': 1}
plt.rcParams.update(params)



def plot_benchmark_results(results):
    f, axarr = plt.subplots(3, 1, facecolor=[0.1, 0.1, 0.1])
    f.tight_layout()
    for idx, ax in enumerate(axarr):
        ax.set(facecolor=[0.2, 0.2, 0.2])

    axarr[0].set(title='Stim duration (ms)')
    axarr[0].plot([x*1000 for x in results['Stim duration']], color='red', label='Stim duration')
    axarr[0].plot([x*results['Ms per frame'] for x in results['Number frames per stim']],
                  color=[0.75, 0.75, 0.75], label='Calculated duration')

    axarr[1].set(title='Frame draw duration avg and std per stimulus (ms)', ylim=[0, 20])
    axarr[1].plot(results['Draw duration avg'], color='green', label='Draw duration avg')
    axarr[1].plot(results['Draw duration std'], color=[0.4, 0.4, 0.8], label='Draw duration std')
    axarr[1].axhline(results['Ms per frame'], color=[.6, .6, .6], label='Ms per frame')

    axarr[2].set(title='Stim ON duration (ms)', ylim=[950, 1050])
    axarr[2].plot([x*1000 for x in results['On time duration']], color='blue', label='On duration')

    for ax in axarr:
        legend = ax.legend(frameon=True)
        frame = legend.get_frame()
        frame.set_facecolor([0.1, 0.1, 0.1])

    plt.show()


    a = 1
