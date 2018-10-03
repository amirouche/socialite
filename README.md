# socialiter - wanna be private-first social network

**step-by-step**

[![travis](https://api.travis-ci.com/amirouche/socialiter.svg?branch=master)](https://travis-ci.com/amirouche/socialiter) [![codecov](https://codecov.io/gh/amirouche/socialiter/branch/master/graph/badge.svg)](https://codecov.io/gh/amirouche/socialiter)

socialiter is proof-of-concept social network that experiments various
backend architectural choices.

<!-- It takes inspiration from peer-to-peer systems ideas and apply them in the context of controlled environments. -->

socialiter is built using the Model-View-Controller pattern on top of
[aiohttp](https://aiohttp.readthedocs.io/en/stable/). The
[jinja2](http://jinja.pocoo.org/) library is used for rendering the
view.

socialiter wants to proove that a complex application can be developed
and operated more easily as a monolithic service using the right
abstractions. That's why socialiter use
[FoundationDB](https://apple.github.io/foundationdb/).

<!-- socialiter experiment with an innovative [distributed **priority** task -->
<!-- queue](https://github.com/amirouche/socialiter/issues/14). The goal of -->
<!-- that particular component is to ease operation of the application. -->

## Getting started

If you are on ubuntu or other debian derivatives try the following:

```sh
make install
```

For other distribution it's recommended to use LXC and install Ubuntu
18.04.

## ROADMAP

- 2018/10/03 - What Are The Civilian Applications

	- Continous Integration
	- Basic Data Persistence
	- Example use of `sparky.py` see `stream.py`
	- Baisc Feed Reader

- 2018/10/XY - [Pick a Culture ship at random](http://bryanschuetz.github.io/culture-namer/)

	- Basic Task queue [TODO]
	- Example Unit Test that mocks a coroutine [TODO]
	- Basic TODO
	- Basic Wiki
	- Basic Forum
	- Basic Paste
	- CSRF Protection
	- Basic Search Engine with a crawler
	- Deploy [TODO]

## Functions for the win

socialiter use a lot of functions.  There is nothing wrong with
classes.  In particular there is no Object Data Mapper (ODM) or Object
Relational Mapper (ORM) abstraction, yet.

That said, socialiter rely on
[trafaret](https://github.com/Deepwalker/trafaret/) for data
validation which is built using classes. Also socialiter make use of
`SocialiterException` class that you can inherit.

## Database

Socialiter rely on [FoundationDB](https://foundationdb.org/) (FDB) to
persist data to disk.  Becareful the default configuration use the
in-memory backend.  The goal with this choice is double:

- Experiment with higher level database abstractions (called layers
  FDB jargon) on top the versatile ordered key-value store offered by
  FDB.

- Experiment operations of FDB from development to deployement of
  single machine cluster to multiple machine clusters.

`src/socialiter/sparky.py` offers an abstraction similar to rdf /
SPARQL. It implements a subset of the standard that should be very
easy to pick.

To get started you can read [FDB's documentation about the Python
client](https://apple.github.io/foundationdb/index.html). Mind the
fact that socialiter rely on
[found](https://github.com/amirouche/asyncio-foundationdb) that is
asyncio driver for FDB based on cffi (which is the recommeded way to
interop with C code by PyPy).

Of course it would be very nice to have well-thought, easy to use,
with migration magics. socialiter proceed step-by-step.  Implement,
use, gain knowledge, then build higher level abstractions.  When
things seem blurry, do not over think it and try something simple to
get started.

### `sparky`

`sparky` is small RDF-like layer which support a subset of SPARQL.

Simply said, it's a triple-store.

Let's try again.

Simply said, sparky stores a **set** of 3-tuples of primitive
datatypes (`int`, `float`, `tuples`, `str` and `bytes` (ie. `dict` is
not supported as-is)) most commonly described as:

```python
(subject, predicate, object)
```

But one might have an easier time mapping that machinery to:

```python
(uid, key, value)
```

The difference with a document store is that tuples are very unique!
Which makes sense since it is a **set** ot tuples. Otherwise said, you
can have the following three tuples in the same database:

```python
("P4X432", "title", "hyperdev.fr")
("P4X432", "SeeAlso", "julien.danjou.info")
("P4X432", "SeeAlso", "blog.dolead.com")
```

This is not possible in document-store because the `SeeAlso` appears
twice.

Querying in RDF land happens via a language "similar" to SQL that is
called SPARQL. Basically, it's pattern matching with bells and
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
patterns = [
	(sparky.var('blog'), 'title', 'hyperdev.fr'),
	(sparky.var('post'), 'blog', sparky.var('blog')),
	(sparky.var('post'), 'title', sparky.var('title')),
]
out = await sparky.where(db, *patterns)
```

That is you can do regular `SELECT` without joins or a `SELECT` with
multiple joins in a single declarative statment. See the [unit tests
for examples](https://bit.ly/2oVz735).

See this [superb tutorial on SPARQL at
data.world](https://docs.data.world/tutorials/sparql/).

The roadmap is to implement something like
[datomic](https://www.datomic.com/) without versioning.

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
