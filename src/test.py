import asyncio
from backend.graphrag.query.local_search import GraphragLocalSearch
from backend.graphrag.query.global_search import GraphragGlobalSearch
graph=GraphragGlobalSearch()
async def main():
   answer= await graph.global_search("Rối loạn nhịp thất là gì")
   print(answer)
   

asyncio.run(main())
