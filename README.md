# socialite - wanna be private-first social network

**step-by-step**

[![travis](https://api.travis-ci.com/amirouche/socialite.svg?branch=master)](https://travis-ci.com/amirouche/socialite) [![codecov](https://codecov.io/gh/amirouche/socialite/branch/master/graph/badge.svg)](https://codecov.io/gh/amirouche/socialite)

socialite is proof-of-concept social network that experiments various
backend architectural choices.

<!-- It takes inspiration from peer-to-peer systems ideas and apply them in the context of controlled environments. -->

socialite is built using the Model-View-Controller pattern on top of
[aiohttp](https://aiohttp.readthedocs.io/en/stable/). The
[jinja2](http://jinja.pocoo.org/) library is used for rendering the
view.

socialite wants to proove that a complex application can be developed
and operated more easily as a monolithic service using the right
abstractions. That's why socialite use
[FoundationDB](https://apple.github.io/foundationdb/).

<!-- socialite experiment with an innovative [distributed **priority** task -->
<!-- queue](https://github.com/amirouche/socialite/issues/14). The goal of -->
<!-- that particular component is to ease operation of the application. -->

## ROADMAP

- 2018/09/30 - What Are The Civilian Applications

	- Continous Integration [DONE]
	- Basic Data Persistence [DONE]
	- Example use of `collection.py` see `stream.py` [DONE]
	- Basic Task queue [TODO]
	- Example use of `sparky.py` see `reader.py` [TODO]
	- Example Unit Test that mocks a coroutine [TODO]
	- Deploy [TODO]

- 2018/10/XY - [Pick a Culture ship at random](http://bryanschuetz.github.io/culture-namer/)

	- Basic TODO
	- Basic Wiki
	- Basic Forum
	- Basic Paste
	- CSRF Protection
	- Basic Search Engine with a crawler

## Functions for the win

socialite use a lot of functions.  There is nothing wrong with
classes.  In particular there is no Object Data Mapper (ODM) or Object
Relational Mapper (ORM) abstraction, yet.

That said, socialite rely on
[trafaret](https://github.com/Deepwalker/trafaret/) for data
validation which is built using classes. Also socialite make use of
`SocialiteException` class that you can inherit.

## Database

Socialite rely on [FoundationDB](https://foundationdb.org/) (FDB) to
persist data to disk.  Becareful the default configuration use the
in-memory backend.  The goal with this choice is double:

- Experiment with higher level database abstractions (called layers
  FDB jargon) on top the versatile ordered key-value store offered by
  FDB.

- Experiment operations of FDB from development to deployement of
  single machine cluster to multiple machine clusters.

There is so far two layers:

- `src/socialite/collection.py` offers an api similar to mongodb.
- `src/socialite/sparky.py` offers an abstraction similar to rdf /
  sparql. It implements a subset of the standard that should be very
  easy to get started.

`sparky` is the prefered layer.

Both implementation are very naive. More detailed description
below. Also, both implementation do no rely on FDB's
[`Subspace`](https://apple.github.io/foundationdb/api-python.html#subspaces)
and
[`Directory`](https://apple.github.io/foundationdb/api-python.html#directories)
class.

To get started you can read [FDB's documentation about the Python
client](https://apple.github.io/foundationdb/index.html). Mind the
fact that socialite rely on a fork of
[found](https://github.com/amirouche/found) that is asyncio driver FDB
based on cffi (which is the recommeded way to interop with C code by
PyPy).

Of course it would be very nice to have single well-thought, easy
to use, with migration magics. socialite proceed step-by-step.
Implement, use, gain knowledge, then build higher level abstractions.
When things seem blurry, do not over think it and try something
simple to get started.

Follows a description and roadmap of the layers in socialite.

### `collection`

`collection` offers an abstraction that is more like document store a
la mongodb. That is it stores JSON-like documents serialized with
`msgpack` in a key-value pair where the key is the an identifier
guaranteed to be unique in the collection. The implementation is naive
in the sense that there is not support for creating or using indices.
The [`collection.query(tr, collection,
**where)`](https://bit.ly/2wZB5TK) coroutine rely on
`collection.all()` coroutine to do the filtering. The complexity in
the worst case is O(n*m) where n is the number of documents in the
collection and m the number of key-value pair in the `where`
parameter.  It only support exact match lookup.

Have look at the [unit tests of collection.py](https://bit.ly/2N47IdI)
for a quick glimpse.

If you choose to use that layer, mind the fact that sorting and
filtering must happen inside a transaction. That is inside a coroutine
decorated with [`fdb.transactional`](https://bit.ly/2wVFuqO) in order
to allow future optimization; if any.

The roadmap of this layer is as simple as to implement the exact same
interface as [pymongodb
drivers](http://api.mongodb.com/python/current/tutorial.html). Since
MongoDB is open-source, one can have a look at how it's actually done
and almost map one-to-one to FDB API since
[MongoDB](https://github.com/mongodb/mongo) rely also on a key-value
storage engine. Simply said, one must implement the following indices:

- exact match
- range / sort lookup
- compound
- full-text search (see python-whoosh)
- geospatial (see the forum
  [[1]](https://bit.ly/2oW0hXS)[[2]](https://bit.ly/2CBa4vO) and the
  documentation)

And the machinery that allows to link a given index to its collection
upfront and on-the-fly indices. Don't forget to update the index in
case of `collection.update` or `collection.delete` is called!

### `sparky`

`sparky` is small RDF-like layer which support a subset of SparQL.

Simply said, it's a quad-store.

Let's try again.

Simply said, it stores a **set** of 4-tuples of primitive datatypes
(`int`, `float`, `tuples`, `str` and `bytes` (ie. `dict` is not
supported as-is)) most commonly described as:

```python
(graph, subject, predicate, object)
```

But one might have an easier time mapping that machinery to the easier
to the mind when you come from MongoDB:

```python
(collection, uid, field, value)
```

The difference with a document store is that tuples are very unique!
Which makes sense since it is a **set** ot tuples. Otherwise said, you
can have the following three tuples in the same database:

```python
("blog", "P4X432", "title", "hyperdev.fr")
("blog", "P4X432", "SeeAlso", "julien.danjou.info")
("blog", "P4X432", "SeeAlso", "blog.dolead.com/")
```

This is not possible in document-store because the `SeeAlso` appears
twice.

Querying in RDF land happens via a language "similar" to SQL that is
called SparQL. Basically, it's pattern matching with bells and
dragons... That being said, sparky implements only the pattern
matching part which makes coding things like the following SQL query:

```sql
SELECT post.title
FROM blog, post
WHERE blog.title='hyperdev.fr'
    AND post.blog_id=blog.id
```

Here is the equivalent using sparky:

```python
query = [
	('blog', sparky.var('blog'), 'title', 'hyperdev.fr'),
	('post', sparky.var('post'), 'blog', sparky.var('blog')),
	('post', sparky.var('post'), 'title', sparky.var('title')),
]
out = await sparky.where(db, *query)
```

That is you can do regular `SELECT` without joins or a `SELECT` with
multiple joins in a single declarative statment. See the [unit tests
for examples](https://bit.ly/2oVz735).

The roadmap is to implement something like
[datomic](https://www.datomic.com/) without versioning.

The current implementation is very naive but the API is (almost) set.
Basically, going further means implementing a cost / statistic based
query planner.  That said, for the time being we will not rely on
explicit indexing but instead index-all-the-things. Another machinery
**might** be put to good use that is [inspired from Gremlin and
implemented in AjguDB](https://bit.ly/2CEc72q), if one can make `async
for` in a transaction work without leaks.

Mind the fact, that since sparky use `fdb.pack` for serialiazing a
tuple items, lexicographic ordering is preserved. That is, one can
defer complex indexing to upper layer namely the application ;]

## Styles Style Guide

- Do no rely on LESS or SASS
- Only rely on classes and tags
- Avoid class when tag is sufficent to disambiguate
- Prefix class names with component name to avoid any leak
- Avoid cascade ie. all styles must appear in the class declaration (ie. it is not DRY)
- When it makes sens, be precise in the selector (most of the time it must start with `#root.root-class`)
