# Assignment 2: Chunking tradeoffs

**Section:** 3. Retrieval-Augmented Generation (RAG)

Run the same document set through two different chunking strategies (e.g., 200 vs. 800 tokens, with/without overlap) and compare retrieval quality on the same 5 test questions. Document which strategy worked better and why.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (screenshots, output, or links)
- [x] Result and what I learned

## Approach

Run with `python experiments.py a2` in `rag_app/`. The same 7 docs and the same 8 questions were run through four chunking configs, measured with two retrievers (TF-IDF keyword and dense embeddings).

Metric: **hit@k**, meaning the exact fact needed to answer is inside one of the top-k chunks. I also recorded how many words the top-1 chunk contains, as a proxy for noise sent to an LLM.

The assignment's 200 vs 800 tokens was scaled down to 25 vs 80 words because the documents are only 70 to 90 words long.

## Evidence

| config | chunks | TF-IDF hit@1 | TF-IDF hit@3 | dense hit@1 | dense hit@3 | avg words in top-1 chunk |
|---|---|---|---|---|---|---|
| 25 words, overlap 0 | 25 | 3/8 | 4/8 | 3/8 | 5/8 | 24 |
| 25 words, overlap 5 | 30 | 3/8 | 5/8 | 4/8 | 7/8 | 25 |
| 80 words, overlap 0 | 10 | 7/8 | 7/8 | 7/8 | 8/8 | 73 |
| 80 words, overlap 15 | 10 | 7/8 | 7/8 | 7/8 | 8/8 | 69 |

## Result and what I learned

- **Winner on this data: 80 words.** hit@1 went from 3/8 to 7/8 for both retrievers.
- **Why small chunks lost:** a 25-word window cuts facts in half (for example "quantity multiplied by unit_price" is split across two chunks), so the answer is never fully inside one chunk.
- **Overlap helped where chunks are small.** At 25 words, overlap 5 raised dense hit@3 from 5/8 to 7/8, because a fact cut at a boundary now survives in the neighbouring chunk. At 80 words it changed nothing, as each chunk already holds nearly a whole document.
- **The trade-off hit@k hides:** with 80-word chunks, top-1 returns about 73 words to answer a one-sentence question. In a real LLM prompt that costs tokens and can distract the model. Hit rate rewards large chunks, so it must be read together with chunk length.
- **Caveat:** this is a tiny corpus (about 500 words), so the result mostly reflects document length. With long real documents I would expect the optimum to move to a middle size, and I would need to repeat the test there.

## Notes

