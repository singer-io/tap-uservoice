## kickoff call notes

Things I need:

- [ ] API Token for a dummy account if one exists, and a set for a real account

Prompts for Rich:

- Replication strategy questions?
- Getting it into Stitch discussion



Rate Limiting
API requests have per minute rate limiting. Each request counts toward your limit. In addition, in order to account for expensive endpoints that tax our servers more, if the request takes longer than 1 second to compute then another “request” is counted for every whole second after the first.

If you are above your limit your requests will return a 429 HTTP error response.

Every request returns the following HTTP headers:

X-Rate-Limit-Limit: The amount of requests available every minute
X-Rate-Limit-Remaining: The amount of requests remaining this period
X-Rate-Limit-Reset: The unix epoch in seconds when the limit resets


When you get the first page of results, if cursor-based pagination is supported, there will be a cursor value in the pagination part of the response. Pass this cursor value as a parameter to the same endpoint to retrieve the next page of results along with a new cursor value.

Example:

GET /api/v2/admin/suggestions?sort=-supporters_count

{
    "suggestions": [ … ],
    "pagination": {
        "total_records": 200,
        "total_pages": 10,
        "page_size": 20,
        "page": 1,
        "cursor": "eyJzb3J0IjoiIiwidmFsIjoyNjMsImxhc3RfaWQiOjIzMTUyMjJ9"
    }
}

GET /api/v2/suggestions?cursor=eyJzb3J0IjoiIiwidmFsIjoyNjMsImxhc3RfaWQiOjIzMTUyMjJ9&sort=-supporters_count

{
    "suggestions": [ … ],
    "pagination": {
        "total_records": 200,
        "total_pages": 10,
        "page_size": 20,
        "page": 1,
        "cursor": "eyJzb3J0IjoiIiwidmFsIjoxNzgsImxhc3RfaWQiOjIwODc3OX0="
    }
}
