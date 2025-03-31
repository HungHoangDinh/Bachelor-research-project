import asyncio
from backend.graphrag.query.local_search import GraphragLocalSearch
graph=GraphragLocalSearch()
async def main():
   answer,cite= await graph.local_search("Rối loạn nhịp thất là gì")
   print(answer)
   print(cite)

asyncio.run(main())
