import matplotlib.pyplot as plt
from program_constants import *

# -*- coding: UTF-8 -*-
__author__ = "KnifeF"


def filter_groups(groups):
    # filter groups ids that found in a local text file
    known_groups = text_from_file(os.path.join(PATH_GROUPS, "group_ids.txt"))
    if known_groups:
        found_groups = 0
        for index in list(groups):
            if index in known_groups:
                found_groups += 1
        sum_all = len(list(groups))
        groups_percent = str(round((found_groups/sum_all)*100))
        groups_percent_str = groups_percent+r"% of profile's groups, " \
                                            r"are matched with given group ids"
        filtered_categories = {'Matched Groups': found_groups, 'Other Groups': sum_all - found_groups}
        filtered_categories = {k: v for k, v in filtered_categories.items() if v != 0}
        return groups_percent_str, filtered_categories, sum_all
    return None, None, None


def filter_by_work(works):
    # filter friends that are working in security
    sum_all = len(list(works))
    security = works.str.contains(SECURITY_KW).sum()
    security_percent = str(round((security/sum_all)*100))
    security_percent_str = r"At least "+security_percent+r"% of profile's friends, are working in security"
    filtered_categories = {'Security Friends': security, 'Other Friends': sum_all - security}
    filtered_categories = {k: v for k, v in filtered_categories.items() if v != 0}
    return security_percent_str, filtered_categories, sum_all


def plot_donut_chart(all_categories, sum_all, path_name, describe_plot):
    # create donut chart from relevant pages categories (liked by the profile)
    if all_categories and sum_all:
        keys_lst = list(all_categories.keys())
        if keys_lst:
            if len(keys_lst) > 1:
                values_lst = list(all_categories.values())
                security_categories = sum(values_lst)

                sizes = []
                for index in range(len(keys_lst)):
                    tmp_key = keys_lst[index]
                    tmp_frac = (all_categories[tmp_key] / security_categories)*100
                    sizes.append(tmp_frac)

                if sizes:
                    # Pie chart

                    # colors
                    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ffb3e6']
                    fig1, ax1 = plt.subplots()
                    plt.title('Total %s: %d' % (describe_plot, sum_all), loc='left', color='black', fontweight="bold")
                    ax1.pie(sizes, pctdistance=1.15, colors=colors, autopct='%1.1f%%', startangle=90)
                    # draw circle
                    centre_circle = plt.Circle((0, 0), 0.60, fc='white')
                    fig = plt.gcf()
                    fig.gca().add_artist(centre_circle)
                    # Equal aspect ratio ensures that pie is drawn as a circle
                    plt.axis('equal')
                    plt.legend(keys_lst, loc=(-0.05, 0.05), shadow=True)
                    plt.tight_layout()
                    plt.savefig(path_name, bbox_inches='tight')


def filter_page_categories(categories):
    # filter page's categories - to create donut chart of profile's interests
    sum_all = sum(categories.value_counts())

    security = categories.str.contains(r'Security|Another pattern').sum()
    forces = categories.str.contains(r'Government Organization|'
                                     r'Police|Armed Forces|Another pattern').sum()
    news = categories.str.contains(r'News|Media|Journalist|TV Channel|TV Network').sum()
    public_figure = categories.str.contains(r'Public Figure').sum()
    other_categories = sum_all - (security+forces+news+public_figure)

    filtered_categories = {'Security': security,
                           'Gov': forces, 'News & Media': news,
                           'Public Figure': public_figure, "Other": other_categories}

    filtered_categories = {k: v for k, v in filtered_categories.items() if v != 0}
    return filtered_categories, sum_all
