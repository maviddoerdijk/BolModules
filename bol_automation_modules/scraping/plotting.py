import matplotlib.pyplot as plt
import os

from testing_validation import create_mock_top_keywords

def plot_top_keywords(topkeywords, n, importance=None):
	"""
	Plots the top n keywords based on their importance and saves the plot to /plots/.
	
	Parameters:
	topkeywords (TopKeywords): An object of the TopKeywords class.
	n (int): The number of top keywords to plot.
	"""
	# Filter keywords by the specified importance level
	if importance:
		filtered_keywords = [kw for kw in topkeywords.keywords_data if kw['importance'] <= importance]
	else:
		filtered_keywords = topkeywords.keywords_data.copy()

	if n == -1:
		n = len(filtered_keywords)

	if n > len(filtered_keywords):
		raise ValueError(f"n is greater than the number of available keywords with the specified importance level.")
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
	plt.xlabel('Maandelijks Zoekvolume')
	plt.title(f"Top Zoekwoorden voor dit product")
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
    plot_top_keywords(mock_top_keywords, 15)