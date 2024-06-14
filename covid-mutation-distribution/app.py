# imports
from functools import partial # for adding a navbar
from shiny.express import input, render, ui # interactivity
from shiny import reactive # reactivity (i.e. calculations)
from shiny.ui import page_navbar # for adding a navbar
import plotly.graph_objects as go # graph
from shinywidgets import render_widget # rendering graph
import functions # functions from functions.py
import re # regex
from pathlib import Path
import faicons

ui.page_opts(
    title="SARS-CoV-2 Mutation Distribution Profiler",
    page_fn=partial(page_navbar, id="page"),
    fillable=True
)
# add dark mode switch to navbar
ui.nav_spacer()
with ui.nav_control():
        ui.input_dark_mode() # << 
        
# Name of application tab
with ui.nav_panel("Home"):
    with ui.card(): 
        ui.markdown(
        '''
        Given a user-provided set of SARS-CoV-2 nucleotide mutations, this application compares the probability of generating this set from the following four distributions:
        - Mutations observed during the first nine months of the pandemic (pre-VoC) (global pre-VoC distribution)
        - Mutations observed during the Omicron era (global Omicron distribution)
        - Mutations observed in chronic infections (chronic distribution)
        - Mutations observed in zoonotic spillovers from humans to white-tailed deer (deer distribution)
        
        In addition, the application will inform the user if the mutation pattern is:
        - Consistent with molnupiravir use (via examination of the transition:transversion ratio)
        - A mutator lineage (contains a mutation that is known to increase the mutation rate of the lineage)
        
        See Application Notes tab for more information.
        '''    
        )
    # layout of columns on first tab
    with ui.layout_columns(col_widths=(4, 8)):
        # first column (or "card")
        with ui.card():
            # variables defined by user input
            # bin size
            ui.input_select("var", "Select Bin Size", 
                    choices= ['genes_split', 'gene', int(500), int(1000)])
            # nucleotide positions where mutations occur - example is shown by default
            ui.input_radio_buttons(
                'var2',
                'Please select a lineage whose mutation distribution you would like to visualize',
                {'C897A, G3431T, A7842G, C8293T, G8393A, G11042T, C12789T, T13339C, T15756A, A18492G, ins21608, C21711T, G21941T, T22032C, C22208T, A22034G, C22295A, C22353A, A22556G, G22770A, G22895C, T22896A, G22898A, A22910G, C22916T, del23009, G23012A, C23013A, T23018C, T23019C, C23271T, C23423T, A23604G, C24378T, C24990T, C25207T, A26529C, A26610G, C26681T, C26833T, C28958A':'BA.2.86',
                 'C1059T, C2388T, C4113T, C4206T, A6377ins, C7029T, C7764T, C9611T, C9711T, C9712T, A10323G, C12213T, C12596T, C12756T, C12786T, A14041G, C14408T, G14557T, G17278T, G18546T, C18646T, G19891T, A21203G, C21707T, C21846T, G21989del, T23020G, A23064C, A23403G, G25563T, T26047G, C26455T, G27996T, G28209T, C28775T, T28889C, C29445T, C29666T':'B.1.641',
                 '1':'I want to enter my own list of lineage-defining mutations'}
            )
            with ui.panel_conditional("input.var2 === '1'"):
                ui.input_text_area("var4", "Please enter a comma-separated list of the lineage-defining mutations (using genomic nucleotide position, example shown)", 
                                        "C897A, G3431T, A7842G, C8293T, G8393A, G11042T, C12789T, T13339C, T15756A, A18492G, ins21608, C21711T, G21941T, T22032C, C22208T, A22034G, C22295A, C22353A, A22556G, G22770A, G22895C, T22896A, G22898A, A22910G, C22916T, del23009, G23012A, C23013A, T23018C, T23019C, C23271T, C23423T, A23604G, C24378T, C24990T, C25207T, A26529C, A26610G, C26681T, C26833T, C28958A",autoresize=True,)

            # colour palette
            ui.input_select("var3", "Select Palette",
                    choices= ["plasma", "viridis", "inferno", "seaborn"])

        # second column (or "card")
        with ui.card():
            @reactive.calc
            def number_of_mutations():
                # return the number of mutations that the user has entered
                if input.var2() != '1':
                    if input.var2().split(',') == ['']:
                        return 0
                    else:
                        return len(input.var2().split(','))
                else:
                    if input.var4().split(',') == ['']:
                        return 0
                    else:
                        return len(input.var4().split(','))
            @render.text
            def print_mutations():
                return f'You have entered {number_of_mutations()} mutations.'
            with ui.layout_column_wrap(width=1/2):
                with ui.card():
                    "Transition to Transversion Ratio"
                    @reactive.calc
                    def get_transition_transversion_ratio():
                                # gui accepts input as a string, so it first needs to be split into a list 
                                # splits occur wherever there is a comma
                                # then pass to function defined in functions.py
                                # to get number of transitions, transversions
                        if input.var2() != '1':
                            transitions, transversions = functions.transition_or_transversion(input.var2().split(','))
                        else:
                            transitions, transversions = functions.transition_or_transversion(input.var4().split(','))
                        return transitions, transversions
                            
                    @render_widget
                            # function to plot transition/transversion ratio heatmap
                    def heatmap():
                        transitions, transversions = get_transition_transversion_ratio()
                        fig2 = go.Figure()
                        config = {'displayModeBar': False}
                        fig2.add_trace(go.Heatmap(
                            z=[[float(transitions)/float(transversions)]],
                            text=[[f'{float(transitions)/transversions:.2f}']],
                            texttemplate='%{text}',
                            colorscale='RdBu',
                            textfont={'size':20},
                            zmax=15, zmin=0,
                            hovertemplate='Transition - Transversion Ratio: %{z}',
                            colorbar=dict(
                                title="Ratio",
                                titleside="top",
                                tickmode="array",
                                tickvals=[1, 7, 14],
                                labelalias={1: "Typical", 14: "Molnupiravir-induced"},
                                ticks="outside"
                            )))
                        
                        fig2.update_yaxes(showticklabels=False)
                        fig2.update_xaxes(showticklabels=False)
                        fig2.update_layout(height=150, width=300)
                        
                        # return figure
                        return fig2
                with ui.card():
                    with ui.value_box(
                                showcase=faicons.icon_svg("dna", width="80px"),
                                theme="bg-gradient-blue-purple"
                            ):
                                "Changes at known mutator sites:"
                                
                                @render.ui
                                def mut_lineage():
                                    if input.var2() != '1':
                                        return f'{functions.mut_lineage_parsing(input.var2())}'
                                    else:
                                        return f'{functions.mut_lineage_parsing(input.var4())}'
            with ui.card():
                # shiny won't use file paths in quotes, you have to use pathlib
                # define mutation distributions and total number of mutations for chronic sequences
                chronic_data = Path(__file__).parent / "./data/chronicnucl.tsv"
                chronic, total_chronic = functions.parse_mutation_files(chronic_data)
                # for deer sequences
                deer_data = Path(__file__).parent / "./data/deernucl.tsv"
                deer, total_deer = functions.parse_mutation_files(deer_data)
                # for global sequences
                global_data = Path(__file__).parent / "./data/globalnucl.tsv"
                global_, total_global = functions.parse_mutation_files(global_data)
                
                # for late global sequences
                globallate_data = Path(__file__).parent / "./data/globallatenucl.tsv"
                global_late, total_lateglobal = functions.parse_mutation_files(globallate_data)

                # once nucleotide positions where mutations occur are entered into the text box, these
                # calculations occur reactively
                @reactive.calc
                # function to parse user mutation data input for plotting
                def plot_user_input():
                    # gui accepts input as a string, so it first needs to be split into a list 
                    # splits occur wherever there is a comma
                    if input.var2() != '1':
                        mutated_nucleotide_list = input.var2().split(',')
                    else:
                        mutated_nucleotide_list = input.var4().split(',')
                    # try to remove non-digit characters, then convert each string in list into
                    # a digit
                    try: 
                        int_nuc_list = [re.sub('\D', '', i) for i in mutated_nucleotide_list]
                        mut_nuc_list = [int(i) for i in int_nuc_list]
                    # if this fails, return some dummy data so the plot is still rendered
                    except: return [[0,0,0,0], [1,1,1,1], 1]
                    # otherwise, parse the list of mutation positions into bins based on the size
                    # specified by the user
                    counts, bins0 = functions.make_bins(mut_nuc_list, input.var())
                    # determine the total number of mutations that are in the list supplied by the
                    # user
                    total_counts = sum(counts)
                    # return everything
                    return counts, bins0, total_counts

                # plot out mutation distributions
                @render_widget
                # function to plot graph
                def hist1():
                    # assign x variables
                    x0 = chronic
                    x1 = global_
                    x2 = global_late
                    x3 = deer
                    opacity = 1.0
                    
                    # calculate mutations per user-specified bin size in histogram for each distribution
                    # chronic
                    counts0, bins0 = functions.make_bins(x0,input.var())
                    # global
                    counts1, bins1 = functions.make_bins(x1,input.var())
                    # global late
                    counts2, bins2 = functions.make_bins(x2,input.var())
                    # deer
                    counts3, bins3 = functions.make_bins(x3,input.var())
                    # instatiate figure
                    fig = go.Figure()
                    # add plot of nucleotide positions specified by user
                    fig.add_trace(go.Bar(
                    x=bins0,
                    y=[x/plot_user_input()[2] for x in plot_user_input()[0]], # normalize bin counts by total number of mutations
                    name='user input', # name used in legend and hover labels,
                    marker_color=functions.select_palette(input.var3())[0], # user specifies colour palette
                    opacity=opacity
                    ))
                    # add plot of chronic distribution
                    fig.add_trace(go.Bar(
                    x=bins0,
                    y=[x/total_chronic for x in counts0], # normalize bin counts by total number of mutations
                    name='chronic', # name used in legend and hover labels,
                    marker_color=functions.select_palette(input.var3())[1], # user specifies colour palette
                    opacity=opacity
                    ))
                    # add plot of global distribution
                    fig.add_trace(go.Bar(
                    x=bins0,
                    y=[x/total_global for x in counts1], # normalize bin counts by total number of mutations
                    name='global pre-VoC', # name used in legend and hover labels,
                    marker_color=functions.select_palette(input.var3())[2], # user specifies colour palette
                    opacity=opacity
                    ))
                    # add plot of global late distribution
                    fig.add_trace(go.Bar(
                    x=bins0,
                    y=[x/total_lateglobal for x in counts2],
                    name='global Omicron',
                    marker_color=functions.select_palette(input.var3())[3],
                    opacity=opacity    
                    ))
                    # add plot of deer distribution
                    fig.add_trace(go.Bar(
                    x=bins0,
                    y=[x/total_deer for x in counts3], # normalize bin counts by total number of mutations
                    name='deer', # name used in legend and hover labels,
                    marker_color=functions.select_palette(input.var3())[4], # user specifies colour palette
                    opacity=opacity
                    ))
                    fig.update_layout(
                    title_text='Distribution of Mutations\nAcross Genome', # title of plot
                    xaxis_title_text='Genome Position', # xaxis label
                    yaxis_title_text='Proportion of Mutations', # yaxis label
                    bargap=0.2, # gap between bars of adjacent location coordinates
                    bargroupgap=0.1, # gap between bars of the same location coordinates
                    plot_bgcolor='white' # specify white background
                    )
                    fig.update_yaxes( # make y axes and ticks look pretty
                    mirror=True,
                    ticks='outside',
                    showline=True,
                    linecolor='black',
                    gridcolor='lightgrey'
                    )
                    fig.update_xaxes( # make x axes and ticks look pretty
                    mirror=True,
                    ticks='outside',
                    showline=True,
                    linecolor='black',
                    gridcolor='white'
                    )
                    # return figure
                    return fig
            
            with ui.card():
                @render.text
                def txt():
                    return f'The log likelihoods of your sequence fitting the mutation distributions above are as follows:'
                with ui.layout_column_wrap(width=1/2):
                # once nucleotide positions where mutations occur are entered into the text box, these
                # calculations occur reactively
                    @reactive.calc
                    # function to calculate log likelihoods of user's mutation distribution fitting each 
                    # of the specified mutation distributions
                    def calc_likelihoods():
                        # input user's bin size selection, global mutations, chronic mutations, deer mutations, user's mutations
                        if input.var2() != '1':
                            likelihood_list, most_likely = functions.most_likely(input.var(), global_, global_late, chronic, deer, input.var2())
                        else:
                            likelihood_list, most_likely = functions.most_likely(input.var(), global_, global_late, chronic, deer, input.var4())
                        # return a list of tuples: [(global_likelihood, 'global'), (global_late_likelihood, 'global_late'),(chronic_likelihood, 'chronic'), (deer_likelihood, 'deer')]
                        # and the name of the distribution that the user's list of mutations fits best (e.g. 'chronic')
                        return likelihood_list, most_likely
                    with ui.card():
                    

                        # print text out for the user

                        with ui.value_box(
                            showcase=faicons.icon_svg("globe", width='50px'),
                            theme="bg-cyan",
                            showcase_layout="left center", 
                            max_height='90px'
                        ):
                            "Global pre-VoC"
                            
                            @render.ui
                            def txt1():
                            # if reactive calculations have been performed (i.e. likelihoods have been calculated),
                            # display likelihoods, otherwise prompt user to enter a list of mutated nucleotide positions
                                try:
                                    return f'{calc_likelihoods()[0][0][0]:.2f}'
                                except:
                                    pass
                        # print text out for the user
                        with ui.value_box(
                            showcase=faicons.icon_svg("earth-americas", width="50px"),
                            theme="bg-green",
                            sshowcase_layout="left center", 
                            max_height='90px'
                        ):
                            "Global Omicron"
                            @render.ui
                            def txt2():
                                # if reactive calculations have been performed (i.e. likelihoods have been calculated),
                                # display likelihoods, otherwise don't do anything 
                                try:
                                    return f'{calc_likelihoods()[0][1][0]:.2f}'
                                except:
                                    pass
                    with ui.card():
                        # print text out for the user
                        with ui.value_box(
                            showcase=faicons.icon_svg("head-side-virus", width="50px"),
                            theme="bg-purple",
                            sshowcase_layout="left center", 
                            max_height='90px'
                        ):
                            "Chronic"
                            @render.ui
                            def txt3():
                                # if reactive calculations have been performed (i.e. likelihoods have been calculated),
                                # display likelihoods, otherwise don't do anything 
                                try:
                                    return f'{calc_likelihoods()[0][2][0]:.2f}'
                                except:
                                    pass

                        # print text out for the user
                        with ui.value_box(
                            showcase=faicons.icon_svg("virus-covid", width="50px"),
                            theme="bg-orange",
                            showcase_layout="left center", 
                            max_height='90px'
                        ):
                            "Deer"            
                            @render.ui
                            def txt4():
                                # if reactive calculations have been performed (i.e. likelihoods have been calculated),
                                # display likelihoods, otherwise don't do anything
                                try:
                                    return f'{calc_likelihoods()[0][3][0]:.2f}'
                                except:
                                    pass
                        
            # print text out for the user
            with ui.value_box(
                showcase=faicons.icon_svg("check", width="50px"),
                theme="blue",
            ):
                "Your sequence best fits the following distribution:"
                @render.ui
                def txt5():
                    # if reactive calculations have been performed (i.e. likelihoods have been calculated),
                    # display likelihoods, otherwise don't do anything
                    try:
                        return f'{calc_likelihoods()[1][1]}'
                    except:
                        pass
                @render.ui
                def txt6():

                        more_likely = functions.sci_notation(functions.times_more_likely(calc_likelihoods()[0])[0], sig_fig=1)
                        dist = functions.times_more_likely(calc_likelihoods()[0])[1]
                        return f'({more_likely} times more likely than the {dist} distribution.)'

                
# name of notes tab 
with ui.nav_panel("Application Notes"):
    # markdown of text to appear on second tab page
    ui.markdown(
'''
### Background
SARS-CoV-2 evolution exhibits a strong clock-like signature with mutational changes accumulating over time, but this pattern is punctuated by “saltational changes”, where lineages appear with a higher number of mutations than expected from their divergence time from other lineages ([Neher (2022)](https://academic.oup.com/ve/article/8/2/veac113/6887176)). Such unusual lineages are thought to reflect long passage times within immunocompromised individuals, sharing many of the same signatures seen in chronic infections ([Harari et al. (2022)](https://www.nature.com/articles/s41591-022-01882-4)). 

When unusual lineages arise, however, it is challenging to know the evolutionary history leading to the observed genomic changes.  Other processes, including passage through animals, ([Bashor et al. 2021](https://www.pnas.org/doi/full/10.1073/pnas.2105253118), [Naderi et al. (2023)](https://elifesciences.org/articles/83685)) mutator lineages with error-prone polymerases ([Takeda et al. (2023)](https://doi.org/10.1016/j.isci.2023.106210)), and exposure to mutagens such as molnupiravir ([Gruber et al. (2024)](https://onlinelibrary.wiley.com/doi/10.1002/jmv.29642)), can also leave unusual genomic signatures. 

Given a user-provided set of nucleotide mutations defining an unusual lineage of SARS-CoV-2, this application compares the probability of generating this set from the following four distributions:
- The list of mutations observed during the first nine months of the pandemic, prior to the spread of VoC [Harari et al. (2022)](https://www.nature.com/articles/s41591-022-01882-4).
- The list of mutations observed in Omicron-era sequences by Harari et al., included submission dates only up to 25 May 2022.
- The list of mutations compiled from 27 chronic infections of immunocompromised individuals [Harari et al. (2022)](https://www.nature.com/articles/s41591-022-01882-4).
- The list of mutations inferred from 109 separate zoonotic spillovers from humans to white-tailed deer [Feng et al. (2023)](https://www.nature.com/articles/s41467-023-39782-x). 

In the first paper, the authors demonstrate that specific lineage-defining mutation patterns occur in SARS-CoV-2 genomes that are sequenced from chronic infections vs. mutations that occurred in SARS-CoV-2 genomes sequenced around the globe at the start of the pandemic (before the rise of Variants of Concern (VOCs)). They also analyzed lineage-defining mutation patterns in VOCs, and concluded that “mutations in chronic infections are predictive of lineage-defining mutations of VOCs”.

Feng et al. sequenced hundreds of SARS-CoV-2 samples obtained from white-tailed deer in the United States. They observed Alpha, Gamma, Delta and Omicron VOCs and determined that the deer infections arose from a minimum of 109 separate transmission events from humans. In addition, the deer were then able to transmit the virus to each other. Deer infections resulted in three documented human zoonoses. The SARS-CoV-2 virus displayed specific adaptation patterns in deer, which differ from adaptations seen in humans. 

In addition, the app informs the user whether the data contain signals consistent with:
- Past molnupiravir use: The transition-to-transversion ratio of mutations is calculated in the focal lineage and compared to a background ratio of ~2:1 for SARS-CoV-2 and to case-control cohort studies indicate a ratio of ~14:1 under molnupiravir treatment ([Gruber et al. (2024)](https://onlinelibrary.wiley.com/doi/10.1002/jmv.29642)). A high ratio may thus suggest past exposure to molnupiravir or a similar factor inducing transitions.
- Mutator lineages: The presence of P203L in nsp14 (C18,647T transition results in mutation of P->L) is flagged as a mutation that alters the ExoN proofreading domain and is associated with a doubling of the mutation rate ([Takeda et al. (2023)](https://doi.org/10.1016/j.isci.2023.106210)), which may contribute to the unusual features of the lineage.

### Application Use
This application accepts a list of comma separated nucleotide positions in a SARS-CoV-2 genome where lineage-defining mutations occur. **Lineage-defining mutations are the subset of mutations in a lineage that have occurred since divergence from the larger SARS-CoV-2 tree.** A list of lineage-defining mutations (the “mutation set”) for [pangolin-designated SARS-CoV-2 lineages](https://www.pango.network/) can be found [here](https://github.com/cov-lineages/pango-designation?tab=readme-ov-file). 

The application determines the likelihood of observing the mutation set as a random draw from each distribution (chronic infection, deer-specific mutations, global (pre-VOC) and global (Omicron era)). The log likelihood of observing the mutation set from each distribution is displayed (in natural log units)12.

Because the mutational data sets are sparse, the method bins sites across the genome when calculating likelihoods. The user can define the bin of interest: genes, genes splitting the spike protein into regions of interest, genome split into 500 nucleotide windows, or genome split into 1000 nucleotide windows. For a given bin choice, the log-likelihood of drawing the user-defined mutation set from each distribution is calculated from the multinomial distribution as:
```
sum(log(((distribution bin counts + 1) / sum(distribution bin counts + 1))<sup>user bin counts</sup>))
```
The addition of one to each bin ensures that there are no bins lacking data.

### Notes on Input and Useful Tools
- Your list can be formatted **with** or **without** nucleotide abbreviations. e.g. `C897A, G3431T, A7842G, C8293T,...`  OR `897, 3431, 7842, 8293,...`
- These coordinates MUST be **genomic** coordinates, **not gene** coordinates like `S:G107Y`
- Indels should be reported by including the first position only e.g. `ins21608` **NOT** `ins21608TCATGCCGCTGT`
- If you have an unaligned SARS-CoV-2 genome sequence and would like to use this tool, you must first place it into a phylogeny so that you can detect lineage-defining mutations. To get started, you may wish to access the tools associated with the [UCSC SARS-CoV-2 Genome Browser](https://genome.ucsc.edu/goldenPath/help/covidBrowserIntro.html#data).
- If you would like to convert gene coordinates to nucleotide coordinates, try using Theo Sanderson’s [tool](https://codon2nucleotide.theo.io/).

### Acknowledgements
This application was developed by the Computational Analysis, Modelling and Evolutionary Outcomes ([CAMEO](https://covarrnet.ca/computational-analysis-modelling-and-evolutionary-outcomes-cameo/)) pillar of Canada's Coronavirus Variants Rapid Response Network ([CoVaRR-Net](https://covarrnet.ca/)). Data analysis, code and maintenance of the application are conducted by Erin E. Gill, Fiona S.L. Brinkman, and Sarah Otto. More details are available on VIROLOGICAL POST?

'''
    )
                     


    