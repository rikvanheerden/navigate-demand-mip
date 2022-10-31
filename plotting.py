import matplotlib.pyplot as plt
import pyam

color_map = {
    'historical (IMAGE)': 'black'
}

pyam.run_control().update({'color': {'scenario': color_map, 'model': color_map}})

def generate_legend(ax):
    handles, labels = ax.get_legend_handles_labels()
    leg_dict = {'color': [], 'linestyle': []}
    for i in range(len(labels)):
        label = labels[i].split(' - ')[0]
        if not label in [i[1] for i in leg_dict['color']]:
            leg_dict['color'].append((handles[i], label))
        label = labels[i].split(' - ')[1]
        if not label in [i[1] for i in leg_dict['linestyle']]:
            if label=='historical (IMAGE)':
                handles[i].set_linestyle('-')
                handles[i].set_marker('')
            else:
                leg_dict['linestyle'].append((handles[i], label))
    leg1 = plt.legend([i[0] for i in leg_dict['color']], [i[1] for i in leg_dict['color']], loc='lower left', bbox_to_anchor=(1, 0.5))
    leg2 = plt.legend([i[0] for i in leg_dict['linestyle']], [i[1] for i in leg_dict['linestyle']], loc='upper left', bbox_to_anchor=(1, 0.5))
    for h in leg1.legendHandles:
        h.set_marker('')
        h.set_linestyle('-')
    for h in leg2.legendHandles:
        h.set_color('grey')
    fig = ax.get_figure()
    fig.add_artist(leg1)
    fig.add_artist(leg2)

def generate_plots(
    df,
    variable,
    scenario,
    region,
    startyear = 1970,
    endyear = 2050,
    color = 'scenario',
    use_markers = True,
    rel_baseyear = False,
    include_ref = False,
    include_hist = True,
    fill_between = True,
    final_ranges = True
):

    if isinstance(scenario,tuple):
        scenario_target, scenario_type, scenario_ctax = scenario
        scenario = ''
        for s1, s2, s3 in [(s1,s2,s3) for s1 in scenario_target for s2 in scenario_type for s3 in scenario_ctax]:
            scenario += '|.*' + s1 + '-' + s2
            if not s1 == 'NPi':
                scenario += '_' + s3
        scenario = scenario[1:]
    
    fill_between = fill_between if endyear<=2050 else False

    if include_hist:
        scenario += '|hist'
    histstartyear = 1980
    if include_ref:
        scenario += '|.*ref'
    
    final_ranges = dict(linewidth=5) if final_ranges and color=='scenario' else False

    if color == 'scenario':
        marker = 'model'
    elif color == 'model':
        marker = 'scenario'
    else:
        raise TypeError('Color argument must either be "scenario" or "model".')
    
    data = df.filter(scenario=scenario, regexp=True)
    data = data.filter(variable=variable, region=region)
    data = data.filter(year=range(startyear, endyear+1))
    def scale_to_base(df, baseyear):
        base_value = df[df['year']==baseyear]['value'].iloc[0]
        df['value'] = df['value'].divide(base_value)
        df['unit'] = 'relative to ' + str(baseyear)
        return(df)
    if rel_baseyear:
        data = pyam.IamDataFrame(data.as_pandas(meta_cols=False).groupby(['model', 'scenario'], group_keys=False).apply(scale_to_base, rel_baseyear))
    ax = data.plot(
        color=color,
        marker=marker if use_markers else None,
        fill_between=fill_between,
        final_ranges=final_ranges,
        legend=False if use_markers else None
    )
    plt.grid()
    if include_hist:
        plt.xlim([histstartyear, None])
    if use_markers:
        generate_legend(ax)
    else:
        plt.tight_layout()
    plt.show()