from flask import Flask, render_template, request, session, redirect, url_for
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import plotly.figure_factory as ff

app = Flask(__name__)

@app.route("/",methods=['POST','GET'])
@app.route("/<name>/<int:tid>",methods=['POST','GET'])
def home(name=None,tid=0):
	compare = False

	data_df = pd.read_csv('top_low_tags.csv')
	data_df['plugin_data'] =  data_df['plugin_data'].apply(lambda s: json.loads(s))
	#data_df['keywords_data'] =  data_df['keywords_data'].apply(lambda s: json.loads(s))
	#data_df['g_search'] =  data_df['g_search'].apply(lambda s: json.loads(s))
		

	def rescale(values,new_min = 0, new_max = 127):
		values = [int(v) for v in values]
		output = []
		old_min, old_max = min(values), max(values)
		for v in values:
			new_v = (new_max - new_min) / (old_max - old_min) * (v - old_min) + new_min
			output.append(new_v)
		return output

	if not name:
		name = data_df['name'][0]
		tid = 0
	print(name)
	if name == 'compare':

		cat_com = []
		cat_com.append([r / 100 for r in data_df['per_free'].to_list()])
		cat_com.append([r / 100 for r in data_df['per_premium'].to_list()])
		cat_com.append([(r / 49120) for r in data_df['num_plugins'].to_list()])

		ant_nm = []
		ant_nm.append([round(d,2) for d in data_df['per_free']])
		ant_nm.append([round(d,2) for d in data_df['per_premium']])
		ant_nm.append([d for d in data_df['num_plugins']]) 

		fig_free = ff.create_annotated_heatmap(cat_com, 
			x=data_df['name'].to_list(), 
			colorscale=[[0, 'navy'], [1, 'plum']], 
			y = ['Free plugins in %','Premium Plugins in %','Total Plugins'],
			font_colors = ['white', 'black'],
			annotation_text=ant_nm
			 )
		fig_free.update_layout( title = "comparision between categories",height=300,width=1000,showlegend=True,margin={ 't': 65, 'b': 45, 'l': 45, 'r': 45 })

		figs = []
		cols = ['downloads','num_plugins','rating','rating_count','avg_download']
		titles = ['Downloads of Tags','Number of plugins of Tags','Rating of Tags','Rating Count of Tags','Average downloads per day of Tags']
		for col,title in zip(cols,titles):
			fig = go.Figure()
			fig.add_trace(go.Bar(
					y=data_df[col],
                    x=data_df['name'],
                    text=[round(v,2) for v in data_df[col]],
                    name=col,
				))
			fig.update_layout(width=1000,title=title)
			figs.append(fig.to_json())



		'''fig_ser = px.area()
		for i in range(len(data_df['name'])):
			v = data_df['g_search'][i]
			inter_df = pd.DataFrame({'Date':list(v.keys()),'value':list(v.values())},columns=['Date','value'])
			inter_df['value'] = inter_df['value'].apply(lambda s: int(s))
			inter_df = inter_df.groupby('Date').agg({'value':lambda s: sum(s) / len(s)})
			inter_df.index = pd.to_datetime(inter_df.index) 
			inter_df = inter_df.resample('M').apply(lambda s: sum(s) / len(s))
			fig_ser.add_scatter(
	        		x = list(inter_df.index),
	        		y = inter_df['value'],
	        		text=inter_df['value'],
	        		mode='lines',
	        		name=data_df['name'][i]
	        		)
			fig_ser.update_layout(
	  			xaxis=dict(
	  				rangeselector=dict(
	  					buttons=list([
	  						dict(count=1,
	                     		label="1m",
	                     		step="month",
	                     		stepmode="backward"),
	                		dict(count=6,
	                     		label="6m",
	                    		step="month",
	                     		stepmode="backward"),
			                dict(count=1,
			                     label="YTD",
			                     step="year",
			                     stepmode="todate"),
			                dict(count=1,
			                     label="1y",
			                     step="year",
			                     stepmode="backward"),
			                dict(step="all")
	            		])
	        		),
	        		rangeslider=dict(
	            	visible=True
	        		),
	        		type="date"
	    		)
			)
		fig_ser.update_layout(title='google search trend of tags',showlegend=True,width=1000)'''

		compare = True	
		return render_template('plugin_plot.html',data = data_df,name = name,tid = tid,free_fig = fig_free.to_json(),figs=list(zip(figs,titles)),com = compare)
		''',fig_ser=fig_ser.to_json()'''	
	else:
		
		

		colors = ['dodgerblue',]* 10
		
		fig_down = go.Figure()
	  
		fig_down.add_trace(go.Bar(
		      x = list(data_df['plugin_data'][tid]['install_count'].values()),
		      y = [' '.join(v.split(' ')[:4]) for v in  list(data_df['plugin_data'][tid]['title'].values())], 
		      text = list(data_df['plugin_data'][tid]['install_count'].values()),
		      name = 'Downloads',
		      textposition='auto',
		      orientation='h',
		      marker_color=colors,
		      

		  ))

		colors = ['gold',]* 10
		
		
		fig_down.add_trace(go.Bar(
		      x = list(data_df['plugin_data'][tid]['rating'].values()),
		      y = [' '.join(v.split(' ')[:4]) for v in  list(data_df['plugin_data'][tid]['title'].values())], 
		      text = list(data_df['plugin_data'][tid]['rating'].values()),
		      name = 'Rating',
		      textposition='auto',
		      orientation='h',
		      marker_color=colors,
		      

		  ))

		colors = ['cyan',]* 10
		fig_down.add_trace(go.Bar(
		      x = list(data_df['plugin_data'][tid]['rating_count'].values()),
		      y = [' '.join(v.split(' ')[:4]) for v in  list(data_df['plugin_data'][tid]['title'].values())], 
		      text = list(data_df['plugin_data'][tid]['rating_count'].values()),
		      name = 'Rating Count',
		      textposition='auto',
		      orientation='h',
		      marker_color=colors,
		      

		  ))
		fig_down.update_xaxes(showticklabels=False,tickvals=[t for t in range(13)])
		fig_down.update_layout(title='% Download, Rating and Rating count of plugins of under Tag '+data_df['name'][tid],height=400,width=1000,barmode='stack',showlegend=True)



		'''colors = ['dodgerblue',]* 10
		
		fig_key_down = go.Figure()
	  
		fig_key_down.add_trace(go.Bar(
		      x = list(data_df['keywords_data'][tid]['downloads'].values()),
		      y = [' '.join(v.split(' ')[:4]) for v in  list(data_df['keywords_data'][tid]['downloads'].keys())], 
		      text = list(data_df['keywords_data'][tid]['downloads'].values()),
		      name = 'Downloads',
		      textposition='auto',
		      orientation='h',
		      marker_color=colors,
		      

		  ))

		colors = ['gold',]* 10
		
		
		fig_key_down.add_trace(go.Bar(
		      x = [round(f,2) for f in list(data_df['keywords_data'][tid]['rating'].values())],
		      y = [' '.join(v.split(' ')[:4]) for v in  list(data_df['keywords_data'][tid]['rating'].keys())], 
		      text = [round(f,2) for f in list(data_df['keywords_data'][tid]['rating'].values())],
		      name = 'Rating',
		      textposition='auto',
		      orientation='h',
		      marker_color=colors,
		      

		  ))

		colors = ['cyan',]* 10
		
		
		fig_key_down.add_trace(go.Bar(
		      x = list(data_df['keywords_data'][tid]['rating_count'].values()),
		      y = [' '.join(v.split(' ')[:4]) for v in  list(data_df['keywords_data'][tid]['rating_count'].keys())], 
		      text = list(data_df['keywords_data'][tid]['rating_count'].values()),
		      name = 'Rating Count',
		      textposition='auto',
		      orientation='h',
		      marker_color=colors,
		      

		  ))
		fig_key_down.update_xaxes(showticklabels=False,tickvals=[t for t in range(13)])
		fig_key_down.update_layout(title='% Download, Rating and Rating Count of keywords of under Tag '+data_df['name'][tid],height=400,width=1000,barmode='stack',showlegend=True)
		  
		'''




		fig_plugin = px.area()
		for k,v in data_df['plugin_data'][tid]['download_rate'].items():
			
			inter_df = pd.DataFrame({'Date':list(v.keys()),'value':list(v.values())},columns=['Date','value'])
			inter_df['Date'] = inter_df['Date'].apply(lambda s: pd.to_datetime(s))
			inter_df['value'] = inter_df['value'].apply(lambda s: int(s))

			inter_df = inter_df.resample('M',on='Date').sum()
			  

			    
			fig_plugin.add_scatter(
			        x = list(inter_df.index),
			        y = inter_df['value'],
			        text=inter_df['value'],
			        mode='lines',
			        name=' '.join(data_df['plugin_data'][tid]['title'][k].split(' ')[:4]),
			        
			  )
			fig_plugin.update_layout(
			  xaxis=dict(
			        rangeselector=dict(
			            buttons=list([
			                dict(count=1,
			                     label="1m",
			                     step="month",
			                     stepmode="backward"),
			                dict(count=6,
			                     label="6m",
			                     step="month",
			                     stepmode="backward"),
			                dict(count=1,
			                     label="YTD",
			                     step="year",
			                     stepmode="todate"),
			                dict(count=1,
			                     label="1y",
			                     step="year",
			                     stepmode="backward"),
			                dict(step="all")
			            ])
			        ),
			        rangeslider=dict(
			            visible=True
			        ),
			        type="date"
			    )
			)

		fig_plugin.update_layout(title='top trending plugins and their monthly downloads',showlegend=True,width=1000)

		'''fig_key = px.area()
		for i in range(len(data_df['name'])):
			k,v = list(data_df['keywords_data'][tid]['download_rate'].items())[i]
			
			inter_df = pd.DataFrame({'Date':list(v.keys()),'value':list(v.values())},columns=['Date','value'])
			inter_df['Date'] = inter_df['Date'].apply(lambda s: pd.to_datetime(s))
			inter_df['value'] = inter_df['value'].apply(lambda s: int(s))
			inter_df = inter_df.resample('M',on='Date').sum()
			fig_key.add_scatter(
	        		x = list(inter_df.index),
	        		y = inter_df['value'],
	        		text=inter_df['value'],
	        		mode='lines',
	        		name=k,
	        
	  			)
			fig_key.update_layout(
	  			xaxis=dict(
	  				rangeselector=dict(
	  					buttons=list([
	  						dict(count=1,
	                     		label="1m",
	                     		step="month",
	                     		stepmode="backward"),
	                		dict(count=6,
	                     		label="6m",
	                    		step="month",
	                     		stepmode="backward"),
			                dict(count=1,
			                     label="YTD",
			                     step="year",
			                     stepmode="todate"),
			                dict(count=1,
			                     label="1y",
			                     step="year",
			                     stepmode="backward"),
			                dict(step="all")
	            		])
	        		),
	        		rangeslider=dict(
	            	visible=True
	        		),
	        		type="date"
	    		)
			)
		fig_key.update_layout(title='top trending keywords and their monthly downloads',showlegend=True,width=1000)
		'''

		fig_gr = px.area()
		for i in range(len(data_df['name'])):
			k,v = list(data_df['plugin_data'][tid]['growth_rate'].items())[i]
			inter_df = pd.DataFrame({'Date':list(v.keys()),'value':list(v.values())},columns=['Date','value'])
			
			inter_df['value'] = inter_df['value'].apply(lambda s: float(s))
			inter_df.set_index('Date',inplace=True)
			fig_gr.add_scatter(
	        		x = list(inter_df.index),
	        		y = inter_df['value'],
	        		text=inter_df['value'],
	        		mode='lines',
	        		name=data_df['plugin_data'][tid]['title'][k]
	        		)
			fig_gr.update_layout(
	  			xaxis=dict(
	  				rangeselector=dict(
	  					buttons=list([
	  						dict(count=1,
	                     		label="1m",
	                     		step="month",
	                     		stepmode="backward"),
	                		dict(count=6,
	                     		label="6m",
	                    		step="month",
	                     		stepmode="backward"),
			                dict(count=1,
			                     label="YTD",
			                     step="year",
			                     stepmode="todate"),
			                dict(count=1,
			                     label="1y",
			                     step="year",
			                     stepmode="backward"),
			                dict(step="all")
	            		])
	        		),
	        		rangeslider=dict(
	            	visible=True
	        		),
	        		type="date"
	    		)
			)
		fig_gr.update_layout(title='growth rate of plugins',showlegend=True,width=1000)


		
		fig_mean = go.Figure()

		fig_mean.add_trace(go.Bar(
      		y = list(data_df['plugin_data'][tid]['mean_diff'].values()),
      		x = [' '.join(v.split(' ')[:4]) for v in  list(data_df['plugin_data'][tid]['title'].values())], 
      		text = list(data_df['plugin_data'][tid]['positions'].values()),
      		name = 'Mean diff',
      		textposition='auto'
      		))
		
		fig_mean.update_traces(hovertemplate='%{label}<br>Position : %{text}<br>Mean diff : %{y}')

		fig_mean.update_layout(title='Mean difference of plugin downloads under Tag '+data_df['name'][tid]+' with mean '+str(data_df['downloads'][tid] / data_df['num_plugins'][tid]),width=1000,hoverlabel=dict(bgcolor="white",font_size=16))



		fig_last = go.Figure()

		fig_last.add_trace(go.Bar(
      		y = [int(v.split(' ')[0]) for v in data_df['plugin_data'][tid]['last_updated'].values()],
      		x = [' '.join(v.split(' ')[:4]) for v in  list(data_df['plugin_data'][tid]['title'].values())], 
      		text = list(data_df['plugin_data'][tid]['last_updated'].values()),
      		name = 'Last updated',
      		textposition='auto'
      		))
		
		fig_last.update_traces(hovertemplate='%{label}<br>Position : %{text}<br>Mean diff : %{y}')

		fig_last.update_layout(title='Last updated plugins under Tag '+data_df['name'][tid],width=1000,hoverlabel=dict(bgcolor="white",font_size=16))


		fig_ins = go.Figure()

		fig_ins.add_trace(go.Bar(
      		y = [int(v[:-1].replace(",","")) for v in data_df['plugin_data'][tid]['active_ins'].values()],
      		x = [' '.join(v.split(' ')[:4]) for v in  list(data_df['plugin_data'][tid]['title'].values())], 
      		text = list(data_df['plugin_data'][tid]['active_ins'].values()),
      		name = 'Last updated',
      		textposition='auto'
      		))
		
		fig_ins.update_traces(hovertemplate='%{label}<br>Position : %{text}<br>Mean diff : %{y}')

		fig_ins.update_layout(title='Active installations of plugins under Tag '+data_df['name'][tid],width=1000,hoverlabel=dict(bgcolor="white",font_size=16))


		fig_avg = go.Figure()
		fig_avg.add_trace(go.Bar(
      		y = list(data_df['plugin_data'][tid]['avg_down'].values()),
      		x = [' '.join(v.split(' ')[:4]) for v in  list(data_df['plugin_data'][tid]['title'].values())], 
      		text = [round(v,2) for v in data_df['plugin_data'][tid]['avg_down'].values()],
      		name = 'Downloads per day',
      		textposition='auto'
      		))
		
		fig_avg.update_traces(hovertemplate='%{label}<br>Position : %{text}<br>Mean diff : %{y}')

		fig_avg.update_layout(title='Average downloads per day of plugins under Tag '+data_df['name'][tid],width=1000,hoverlabel=dict(bgcolor="white",font_size=16))



		fig_tab = go.Figure(data=[go.Table(
			header=dict(values=['Plugins','Issues Resolved in last 2 Months']),
			cells=dict(values=[list(data_df['plugin_data'][tid]['title'].values()),list(data_df['plugin_data'][tid]['issue'].values())])

			)])

		

		fig_tab.update_layout(title='Issues resolved of plugins under Tag '+data_df['name'][tid],width=1000)



		


		'''	
		fig_ser = px.area()
		v = data_df['g_search'][tid]
		inter_df = pd.DataFrame({'Date':list(v.keys()),'value':list(v.values())},columns=['Date','value'])
		inter_df['value'] = inter_df['value'].apply(lambda s: int(s))
		inter_df = inter_df.groupby('Date').agg({'value':lambda s: sum(s) / len(s)})
		inter_df.index = pd.to_datetime(inter_df.index) 
		inter_df = inter_df.resample('M').apply(lambda s: sum(s) / len(s))
		fig_ser.add_scatter(
	        	x = list(inter_df.index),
	        	y = inter_df['value'],
	        	text=inter_df['value'],
	        	mode='lines',
	        	name=data_df['name'][tid]
	        	)
		fig_ser.update_layout(
	  		xaxis=dict(
	  			rangeselector=dict(
	  				buttons=list([
	  						dict(count=1,
	                     		label="1m",
	                     		step="month",
	                     		stepmode="backward"),
	                		dict(count=6,
	                     		label="6m",
	                    		step="month",
	                     		stepmode="backward"),
			                dict(count=1,
			                     label="YTD",
			                     step="year",
			                     stepmode="todate"),
			                dict(count=1,
			                     label="1y",
			                     step="year",
			                     stepmode="backward"),
			                dict(step="all")
	            		])
	        		),
	        		rangeslider=dict(
	            	visible=True
	        		),
	        		type="date"
	    		)
			)
		fig_ser.update_layout(title='google search trend of tag',showlegend=True,width=1000)
  		'''
  
  
		


		return render_template('plugin_plot.html',data = data_df,name = name,tid = tid,fig_plugin = fig_plugin.to_json(),fig_down=fig_down.to_json(),fig_gr=fig_gr.to_json(),fig_mean=fig_mean.to_json(),fig_last=fig_last.to_json(),fig_ins=fig_ins.to_json(),fig_tab=fig_tab.to_json(),fig_avg=fig_avg.to_json())
		''',fig_key_down=fig_key_down.to_json(),fig_key=fig_key.to_json(),fig_ser=fig_ser.to_json()'''
	return "oops"




