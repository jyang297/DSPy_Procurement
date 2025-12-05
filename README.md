# DSPy Procurement Agent 

> Jiaqi Yang: jyang297@uottawa.ca
> Linkedin: https://www.linkedin.com/in/jiaqi-yang-b3014424b/
> Portfolio: Incoming!

This project implements an end-to-end procurement decision workflow powered by:

1. DSPy (Refine, Predict, Chain-of-Thought modules)

2. Milvus vector database (Supplier / Audit / Contract retrieval)

3. OpenAI embeddings & LLMs

4. Custom reward functions for schema compliance and budget extraction

# Flowmap
[Flowmap](demo/flowmap_0.1.0)

# Quick Start

The project needs mock data and milvus to launch. You may need to follow the following steps for the demo.
We recomend you to use `uv` to mange python library.
```bash
uv sync
```

You also need to create put your `OPENAI_API_KEY` into `.env`.

You may need to use my `.sh` script for Milvus:
```bash
bash ./MyMilvus/milvus-light.sh start
python milvus_init.py
```

Because we are using OpenAI api calling, we do not recomend anyone to use real data for the test. Please use:

```python
python faker/data_generator.py  
```

for mock data which will be saved in `./mock_data`.

To start the demo, please use 

```python
python ./tests/pipeline_test.py
```

You can type your own task or just leave it alone for a demo task.

# Thanks

If you have any problem, feel free to reach me. Happy to discuss any problem. 
And please notice: This project does not optimize the prompts as the way DSPy devlopers design it