import matplotlib.pyplot as plt
import os

from testing_validation import create_mock_top_keywords

def top_keywords_plot(topkeywords, n):
	"""
	Plots the top n keywords based on their importance and saves the plot to /plots/.
	
	Parameters:
	topkeywords (TopKeywords): An object of the TopKeywords class.
	n (int): The number of top keywords to plot.
	"""
	if n > len(topkeywords.keywords_data):
		raise ValueError(f"n is greater than the number of available keywords.")
	
	# Sort keywords by highest monthly search volume
	sorted_keywords = sorted(topkeywords.keywords_data, key=lambda x: x['monthly_search_volume'], reverse=True)
	
	# Get the top n keywords
	top_n_keywords = sorted_keywords[:n]
	
	# Extract data for plotting
	keywords = [kw['keyword'] for kw in top_n_keywords]
	volumes = [kw['monthly_search_volume'] for kw in top_n_keywords]
	
	# Create the plot
	plt.figure(figsize=(10, 6))
	plt.barh(keywords, volumes, color='skyblue')
	plt.xlabel('Keyword')
	plt.ylabel('Monthly Search Volume')
	plt.title(f'Top {n} Keywords by Importance')
	plt.gca().invert_yaxis()  # Invert y-axis to have the highest importance at the top
	
	# Ensure the plots directory exists
	if not os.path.exists('plots'):
		os.makedirs('plots')
  
	# Rotate keyword labels for better readability
	plt.yticks(rotation=45)
	
	# Save the plot
	title_first_word = topkeywords.product_title.split()[0]
	plt.savefig(f'plots/top_{n}_keywords_{title_first_word}.png')
	plt.close()
	
	# Get the top n keywords
	top_n_keywords = sorted_keywords[:n]
	
	# Extract data for plotting
	keywords = [kw['keyword'] for kw in top_n_keywords]
	volumes = [kw['monthly_search_volume'] for kw in top_n_keywords]
	
	# Create the plot
	plt.figure(figsize=(10, 6))
	plt.barh(keywords, volumes, color='skyblue')
	plt.xlabel('Keyword')
	plt.ylabel('Monthly Search Volume')
	plt.title(f'Top {n} Keywords by Importance')
	plt.gca().invert_yaxis()  # Invert y-axis to have the highest importance at the top
	
	# Ensure the plots directory exists
	if not os.path.exists('plots'):
		os.makedirs('plots')
  
	# Rotate keyword labels for better readability
	plt.yticks(rotation=45)
	
	# Save the plot
	title_first_word = topkeywords.product_title.split()[0]
	plt.savefig(f'plots/top_{n}_keywords_{title_first_word}.png')
	plt.close()
 
if __name__ == "__main__":
    mock_top_keywords = create_mock_top_keywords()
    top_keywords_plot(mock_top_keywords, 15)