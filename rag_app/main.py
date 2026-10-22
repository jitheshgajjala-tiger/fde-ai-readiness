import argparse
import logging

from rag import (
    answer_from_hits,
    build_chunks,
    build_dense_index,
    build_index,
    clean_documents,
    retrieve,
    retrieve_dense,
    retrieve_hybrid,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask questions over the local docs.")
    parser.add_argument("question")
    parser.add_argument("--docs", default="docs")
    parser.add_argument("--chunk-size", type=int, default=80)
    parser.add_argument("--overlap", type=int, default=15)
    parser.add_argument("--top-k", type=int, default=1)
    parser.add_argument("--doc-type", default=None, help="restrict to a docs sub-folder, e.g. sttm")
    parser.add_argument("--retriever", choices=["keyword", "dense", "hybrid"], default="hybrid")
    parser.add_argument("--min-coverage", type=float, default=0.0, help="refuse unless this share of query terms is in the chunk")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    chunks = build_chunks(clean_documents(args.docs), args.chunk_size, args.overlap)
    keyword = build_index(chunks)
    if args.retriever == "keyword":
        hits = retrieve(keyword, args.question, args.top_k, args.doc_type)
    else:
        dense = build_dense_index(chunks)
        if args.retriever == "dense":
            hits = retrieve_dense(dense, args.question, args.top_k, args.doc_type)
        else:
            hits = retrieve_hybrid(dense, keyword, args.question, args.top_k, args.doc_type)
    print(answer_from_hits(args.question, hits, min_coverage=args.min_coverage))


if __name__ == "__main__":
    main()
