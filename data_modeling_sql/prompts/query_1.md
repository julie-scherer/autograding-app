## Query 1: Actors Table DDL

**Assignment Prompt:** 
> Write a DDL query to create an `actors` table with the following fields:
> 1. `actor`: Actor name
> 2. `actor_id`: Actor's ID
> 3. `films`: An array of `struct` with the following fields:
>   - `film`: The name of the film.
>   - `votes`: The number of votes the film received.
>   - `rating`: The rating of the film.
>   - `film_id`: A unique identifier for each film.
> 4. `quality_class`: A categorical bucketing of the average rating of the movies for this actor in their most recent year:
>   - `star`: Average rating > 8.
>   - `good`: Average rating > 7 and ≤ 8.
>   - `average`: Average rating > 6 and ≤ 7.
>   - `bad`: Average rating ≤ 6.
> 5. `is_active`: A BOOLEAN field that indicates whether an actor is currently active in the film industry (i.e., making films this > year).
> 6. `current_year`: The year this row represents for the actor


**Example solution:**

```sql

```
