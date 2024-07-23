Steps initially derived from https://ollama.com/blog/embedding-models

Requirements:
- Python 3: https://www.python.org/downloads/
- cURL: https://curl.se/download.html

1. Download and install Ollama and follow the quick setup instructions: https://ollama.com/download

2. Download the models `mxbai` and `llama3`.

- As of March 2024, **mxbai-embed-large** model archives SOTA performance for Bert-large sized models on the MTEB. It outperforms commercial models like OpenAIs `text-embedding-3-large` model and matches the performance of model 20x its size.
- **Llama 3** (8B) instruction-tuned models are fine-tuned and optimized for dialogue/chat use cases and outperform many of the available open-source chat models on common benchmarks.
- Bonus, if you have a powerful laptop/desktop you might want to swap Llama3 8 billion parameter model for the Llama3 70 billion parameter, which has better inference and more internal knowledge. To use 70B instead use this command `ollama run llama3:70b` (note this is a 40GB download), and change [the line of code in query.py](https://github.com/wikimedia-enterprise/Structured-Contents-LLM-RAG/blob/main/query.py#L67) that loads the `llama3` model to: `model="llama3:70b"`

In a terminal console, type _(Warning, llama3 is a 4.7GB download and mxbai-embed-large is 670MB)_:
```
ollama pull mxbai-embed-large
ollama run llama3
```

3. Verify that Ollama is working and using the model, the output should be a JSON object with an `embedding` array of floating point numbers
```
curl http://localhost:11434/api/embeddings -d '{
  "model": "mxbai-embed-large",
  "prompt": "Summarize the features of Wikipedia in 5 bullet points"
}'
```

4. Clone our demo Repo to get started:
```
git clone https://github.com/wikimedia-enterprise/Structured-Contents-LLM-RAG.git
```

5. Install virtual Python environment, activate it, and install Python packages in `requirements.txt`:
```
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

6. Edit the Environment variables file to add your Wikimedia Enterprise API credentials. Don't have an account yet; [signup for free](https://enterprise.wikimedia.com/signup).
Then rename `sample.env` to `.env` and add your Wikimedia Enterprise username and password:
```
WIKI_API_USERNAME=username
WIKI_API_PASSWORD=password
```
Notes:
- You can skip this next step if you have a slow internet connection and instead use the `/dataset/en.csv` file that has the structured Wikipedia data ready to use in Step 7.

7. Review the Python in `get_dataset.py` which calls the Wikipedia Enterprise On-Demand API for 500 English articles. You can run it with the command:
```
python get_dataset.py
```

Notes:
- In `get_dataset.py`, we are using multithreading to download the dataset, using your CPU Cores to send many requests at one. If you prefer to keep it simple, we have a less complex downloader that downloads the data in sequence, but it takes considerable longer. See the code in `pipelineV1()` and `pipelineV2()`, the first function runs sequentially, the second runs in parallel. Notice we are using thread locking to guarantee that the array is appended without a race condition.
- If you want to use you newly downloaded data rather than the sample dataset in `en.csv`, then rename the file `dataset/en3.csv` (or `dataset/en2.csv` if you ran the sequential pipeline) to `dataset/en.csv`
- One important function in this code is `clean_text()` which parses the HTML tags and extracts the plain text that the LLM model is expecting. Data tidying is a big part of the Machine Learning workflow. Review the code in `clean_text()` so you can understand the text cleaning steps.
- Wikimedia Enterprise has a number of added-value APIs, that give developers easier access to cleaned Wikimedia data. You don't need to be a Data Scientist or AI expert to integrate Wikipedia/Wikidata knowledge into your systems. Visit our [developer documentation portal](https://enterprise.wikimedia.com/docs/) for more API info. 

9. Review the Python in `import.py` which imports the CSV data from step 6 and load it into ChromaDB. Then run it:
```
python import.py
```

10. Review the Python in `query.py` to input your query, query ChromaDB, get the relevant articles and pass it to Llama3 for generating the response.
Run the Streamlit Web UI with:
```
streamlit run query.py
```
Notes:
- There are other more advanced Web UIs for local chat tools if you're interested. For example, if you have Docker installed you can easily run this UI: https://github.com/open-webui/open-webui
```
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

11. You can safely delete all the code and data in this project, there are no other dependencies. You may wish to uninstall Ollama and the LLM models you downloaded. Use these commands:

```
ollama rm mxbai-embed-large
ollama rm llama3
```

## Here are some example chats with RAG turned OFF and then ON:

### Joe that does icosathlon - RAF OFF
!["Joe that does icosathlon" with RAG off](./images/Joe_that_does_icosathlon-off.png)
### Joe that does icosathlon - RAG ON
!["Joe that does icosathlon" with RAG on ](./images/Joe_that_does_icosathlon.png)


### Wlassifoff - RAF OFF
!["Wlassifoff" with RAG off](./images/Wlassikoff-off.png)
### Wlassifoff - RAG ON
!["Wlassifoff" with RAG on ](./images/Wlassikoff.png)

### Newala Town - RAF OFF
!["Newala Town" with RAG off](./images/NewalaTown-off.png)
### Newala Town - RAG ON
!["Newala Town" with RAG on ](./images/NewalaTown.png)

### horse breeds of the British Isles - RAF OFF
!["horse breeds of the British Isles" with RAG off](./images/horse_breeds_of_the_British_Isles-off.png)
### horse breeds of the British Isles - RAG ON
!["horse breeds of the British Isles" with RAG on ](./images/horse_breeds_of_the_British_Isles.png)

### Chow a shooter - RAF OFF
!["Chow a shooter" with RAG off](./images/Chow_a_shooter-off.png)
### Chow a shooter - RAG ON
!["Chow a shooter" with RAG on ](./images/Chow_a_shooter.png)
