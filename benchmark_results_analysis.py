import matplotlib.pyplot as plt
import matplotlib
import datetime
import numpy as np

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




