import matplotlib.pyplot as plt
import datetime


def plotRisks(df, groupbyColumn='Subscription_Name', title='Risk Patterns', xlabel='Azure Subscriptions', ylabel='Number of Risky Rules' ):
    plotData = df.groupby([groupbyColumn]).sum()
    plotData.plot(kind='bar', stacked=True, figsize=(20,10))
    plt.style.use('ggplot')
    plt.legend(bbox_to_anchor=(1.6, 1.05), loc=0)
    plt.title(f"{title}\n{str(datetime.date.today())}\n", fontsize=15)
    plt.ylabel(ylabel, fontsize=12)
    plt.xlabel(xlabel, fontsize=12)  
    plt.show()
    #plt.savefig()

