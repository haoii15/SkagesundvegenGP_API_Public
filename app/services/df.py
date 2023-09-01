import pandas as pd
COLOR = "#36393e"
FONT = "Sans-serif"

def styleDf(df):

    styled = df.style.set_table_styles(
    [{'selector': 'th',
    'props': [('background', COLOR), 
                ('color', 'white'),
                ('font-family', FONT)]},
    
    {'selector': 'td',
    'props': [('font-family', FONT),
                ('color', 'white')]},

    {'selector': 'tr:nth-of-type(odd)',
    'props': [('background', COLOR)]}, 
    
    {'selector': 'tr:nth-of-type(even)',
    'props': [('background', COLOR)]},
    
    ]
    ).hide_index()

    return styled

def listToDf(list):
    df = pd.DataFrame(list, columns = ["rank", "navn", "level", "xp", "meldingar"])
    return styleDf(df)

def llistToDf(list, columns):
    df = pd.DataFrame(list, columns = columns).round(2)
    return styleDf(df)