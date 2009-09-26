# coding=utf-8
r"""
Word paths

A word path is a word represented as a discrete path in a two (or more)
dimensions space using a one-to-one correspondence between the alphabet and
a set of steps.

AUTHORS:

- Arnaud Bergeron (2008) : Initial version, path on the square grid

- Sebastien Labbe (2009-01-14) : New classes and hierarchy, doc and functions.

EXAMPLES:

The combinatorial class of all paths defined over three given steps::

    sage: P = WordPaths('abc', steps=[(1,2), (-3,4), (0,-3)]); P
    Word Paths over 3 steps

This defines a one-to-one correspondence between alphabet and steps::

    sage: d = P.letters_to_steps()
    sage: sorted(d.items())
    [('a', (1, 2)), ('b', (-3, 4)), ('c', (0, -3))]

Creation of a path from the combinatorial class P defined above::

    sage: p = P('abaccba'); p
    Path: abaccba

Many functions can be used on p: the coordinates of its trajectory,
ask whether p is a closed path, plot it and many other::

    sage: list(p.points())
    [(0, 0), (1, 2), (-2, 6), (-1, 8), (-1, 5), (-1, 2), (-4, 6), (-3, 8)]
    sage: p.is_closed()
    False
    sage: p.plot()

Since p is a finite word, many functions from the word library are available::

    sage: p.crochemore_factorization()
    (a, b, a, c, c, ba)
    sage: p.is_palindrome()
    False
    sage: p[:3]
    Path: aba
    sage: len(p)
    7

P also herits many functions from Words::

    sage: P = WordPaths('rs', steps=[(1,2), (-1,4)]); P
    Word Paths over 2 steps
    sage: P.alphabet()
    Ordered Alphabet ['r', 's']
    sage: list(P.iterate_by_length(3))
    [Path: rrr,
     Path: rrs,
     Path: rsr,
     Path: rss,
     Path: srr,
     Path: srs,
     Path: ssr,
     Path: sss]

Some built-in combinatorial classes of paths::

    sage: P = WordPaths('abAB', steps='square_grid'); P
    Word Paths on the square grid

::

    sage: D = WordPaths('()', steps='dyck'); D
    Finite Dyck paths
    sage: d = D('()()()(())'); d
    Path: ()()()(())
    sage: d.plot()

::

    sage: P = WordPaths('abcdef', steps='triangle_grid')
    sage: p = P('babaddefadabcadefaadfafabacdefa')
    sage: p.plot()

Vector steps may be in more than 2 dimensions::

    sage: d = [(1,0,0), (0,1,0), (0,0,1)]
    sage: P = WordPaths(alphabet='abc', steps=d); P
    Word Paths over 3 steps
    sage: p = P('abcabcabcabcaabacabcababcacbabacacabcaccbcac')
    sage: p.plot()

::

    sage: d = [(1,3,5,1), (-5,1,-6,0), (0,0,1,9), (4,2,-1,0)]
    sage: P = WordPaths(alphabet='rstu', steps=d); P
    Word Paths over 4 steps
    sage: p = P('rtusuusususuturrsust'); p
    Path: rtusuusususuturrsust
    sage: p.end_point()
    (5, 31, -26, 30)

::

    sage: CubePaths = WordPaths('abcABC', steps='cube_grid'); CubePaths
    Word Paths on the cube grid
    sage: CubePaths('abcabaabcabAAAAA').plot()

The input data may be a str, a list, a tuple,
a callable or a finite iterator::

    sage: P = WordPaths([0, 1, 2, 3])
    sage: P([0,1,2,3,2,1,2,3,2])
    Path: 012321232
    sage: P((0,1,2,3,2,1,2,3,2))
    Path: 012321232
    sage: P(lambda n:n%4, length=10)
    Path: 0123012301
    sage: P(iter([0,3,2,1]), length='finite')
    Path: 0321

REFERENCES:

- http://en.wikipedia.org/wiki/Regular_tiling

- http://en.wikipedia.org/wiki/Dyck_word
"""
#*****************************************************************************
#       Copyright (C) 2008 Arnaud bergeron <abergeron@gmail.coms>,
#       Copyrigth (C) 2009 Sebastien Labbe <slabqc@gmail.com>,
#
#  Distributed under the terms of the GNU General Public License version 2 (GPLv2)
#
#  The full text of the GPLv2 is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.structure.sage_object import SageObject
from sage.misc.cachefunc import cached_method
from sage.misc.lazy_attribute import lazy_attribute
from sage.combinat.combinat import CombinatorialObject
from sage.combinat.words.words import Words_over_OrderedAlphabet, Words
from sage.combinat.words.word import FiniteWord_class, Word_class
from sage.combinat.words.alphabet import OrderedAlphabet
from sage.plot.plot import arrow, line, polygon, point, Graphics
from sage.modules.free_module_element import vector
from sage.rings.integer import Integer
from sage.rings.all import ZZ, RR, QuadraticField
from word_datatypes import (WordDatatype_str,
                            WordDatatype_list,
                            WordDatatype_tuple)
                            #WordDatatype_cpp_basic_string)

from word_infinite_datatypes import (
                            WordDatatype_iter_with_caching,
                            WordDatatype_iter,
                            WordDatatype_callable_with_caching,
                            WordDatatype_callable)

#######################################################################
#                                                                     #
#                         WordPaths function                          #
#                                                                     #
#######################################################################

def WordPaths(alphabet, steps=None):
    r"""
    Returns the combinatorial class of paths of the given type of steps.

    INPUT:

    - ``alphabet`` - ordered alphabet

    - ``steps`` - (default is None). It can be one of the following:

      - an iterable ordered container of as many vectors as there are
        letters in the alphabet. The vectors are associated to the letters
        according to their order in steps. The vectors can be a tuple or
        anything that can be passed to vector function.

      - ``None``: In this case, the type of steps are guessed from the
        length of alphabet.

      - 'square_grid' or 'square' : (default when size of alphabet is 4)
        The order is : East, North, West, South.

      - 'triangle_grid' or 'triangle':

      - 'hexagonal_grid' or 'hexagon' :(default when size of alphabet is 6)

      - 'cube_grid' or 'cube' :

      - 'north_east', 'ne' or 'NE' : (the default when size of alphabet is 2)

      - 'dyck':

    OUTPUT:

    - The combinatorial class of all paths of the given type.

    EXAMPLES:

    The steps can be given explicitely::

        sage: WordPaths('abc', steps=[(1,2), (-1,4), (0,-3)])
        Word Paths over 3 steps

    Different type of input alphabet::

        sage: WordPaths(range(3), steps=[(1,2), (-1,4), (0,-3)])
        Word Paths over 3 steps
        sage: WordPaths(['cric','crac','croc'], steps=[(1,2), (1,4), (0,3)])
        Word Paths over 3 steps

    Directions can be in three dimensions as well::

        sage: WordPaths('ab', steps=[(1,2,2),(-1,4,2)])
        Word Paths over 2 steps

    When no steps are given, default classes are returned::

        sage: WordPaths('ab')
        Word Paths in North and East steps
        sage: WordPaths(range(4))
        Word Paths on the square grid
        sage: WordPaths(range(6))
        Word Paths on the hexagonal grid

    There are many type of built-in steps...

    On a two letters alphabet::

        sage: WordPaths('ab', steps='north_east')
        Word Paths in North and East steps
        sage: WordPaths('()', steps='dyck')
        Finite Dyck paths

    On a four letters alphabet::

        sage: WordPaths('ruld', steps='square_grid')
        Word Paths on the square grid

    On a six letters alphabet::

        sage: WordPaths('abcdef', steps='hexagonal_grid')
        Word Paths on the hexagonal grid
        sage: WordPaths('abcdef', steps='triangle_grid')
        Word Paths on the triangle grid
        sage: WordPaths('abcdef', steps='cube_grid')
        Word Paths on the cube grid

    TESTS::

        sage: WordPaths(range(5))
        Traceback (most recent call last):
        ...
        TypeError: Unable to make a class WordPaths from Ordered Alphabet [0, 1, 2, 3, 4]
        sage: WordPaths('abAB', steps='square_gridd')
        Traceback (most recent call last):
        ...
        TypeError: Unknown type of steps : square_gridd
    """
    #Construction of the alphabet
    alphabet = OrderedAlphabet(alphabet)

    #If no steps are given, they are guessed from the alphabet
    if steps is None:
        if alphabet.cardinality() == 2:
            steps = 'north_east'
        elif alphabet.cardinality() == 4:
            steps = 'square_grid'
        elif alphabet.cardinality() == 6:
            steps = 'hexagonal_grid'
        else:
            raise TypeError, "Unable to make a class WordPaths from %s"%alphabet

    #Returns the class of WordPaths according to the given type of paths
    if isinstance(steps, str):
        if steps in ('square_grid', 'square'):
            return WordPaths_square_grid(alphabet=alphabet)
        elif steps in ('triangle_grid', 'triangle'):
            return WordPaths_triangle_grid(alphabet=alphabet)
        elif steps in ('hexagonal_grid', 'hexagon'):
            return WordPaths_hexagonal_grid(alphabet=alphabet)
        elif steps in ('cube_grid', 'cube'):
            return WordPaths_cube_grid(alphabet=alphabet)
        elif steps in ('north_east', 'ne', 'NE'):
            return WordPaths_north_east(alphabet=alphabet)
        elif steps == 'dyck':
            return WordPaths_dyck(alphabet=alphabet)
        else:
            raise TypeError, "Unknown type of steps : %s"%steps
    else:
        return WordPaths_all(alphabet=alphabet, steps=steps)

#######################################################################
#                                                                     #
#                  Combinatorial classes of word paths                #
#                                                                     #
#######################################################################

class WordPaths_all(Words_over_OrderedAlphabet):
    r"""
    The combinatorial class of all paths, i.e of all words over
    an alphabet where each letter is mapped to a step (a vector).
    """
    def __init__(self, alphabet, steps):
        r"""
        INPUT:

        - ``alphabet`` - an ordered alphabet

        - ``steps`` - an iterable (of same length as alphabet) of ordered vectors

        EXAMPLES::

            sage: from sage.combinat.words.paths import WordPaths_all
            sage: d = ((1,1), (-1,1), (1,-1), (-1,-1))
            sage: P = WordPaths_all('abAB', d); P
            Word Paths over 4 steps
            sage: P == loads(dumps(P))
            True

        TESTS::

            sage: from sage.combinat.words.paths import WordPaths_all
            sage: d = ((1,1), (-1,1), (1,-1), (-1,-1))
            sage: WordPaths_all('abA', d)
            Traceback (most recent call last):
            ...
            TypeError: size of steps (=4) and alphabet (=3) must be equal

            sage: d = ((1,1), 1)
            sage: WordPaths_all('ab', d)
            Traceback (most recent call last):
            ...
            ValueError: Can't make vectors from steps

            sage: d = ((1,1), (-1,1,0))
            sage: WordPaths_all('ab', d)
            Traceback (most recent call last):
            ...
            ValueError: Can't make summable vectors from steps
        """
        #temporary hack
        alphabet = OrderedAlphabet(alphabet)

        #Construction of the words class
        super(WordPaths_all, self).__init__(alphabet)

        #Checking the size of alphabet and steps
        if len(steps) != alphabet.cardinality():
            raise TypeError,"size of steps (=%s) and alphabet (=%s) must be \
equal"%(len(steps),alphabet.cardinality())

        #Construction of the steps

        from sage.structure.element import Vector
        if all(map(lambda x: isinstance(x, Vector), steps)):
            vsteps = steps
        else:
            try:
                vsteps = map(vector, steps)
            except (TypeError):
                raise ValueError, "Can't make vectors from steps"
        try:
            s = sum(vsteps)
        except (TypeError, AttributeError):
            raise ValueError, "Can't make summable vectors from steps"
        self._steps = dict(zip(alphabet, vsteps))
        self._vector_space = s.parent()

    @lazy_attribute
    def _element_classes(self):
        r"""
        Returns a dictionary that gives the class of the elements of self.

        The word may be finite (infinite or of unknown length is not supported
        yet).
        Its data may be str, list, tuple, a callable or an iterable.
        For callable and iterable, the data may be cached.
        The dimension of the path may be 1, 2, 3 or more.

        TESTS::

            sage: d = WordPaths('ab',steps=[(1,2),(3,4)])._element_classes
            sage: type(d)
            <type 'dict'>
            sage: len(d)
            7
            sage: d['FiniteWord_tuple']
            <class 'sage.combinat.words.paths.FiniteWordPath_2d_tuple'>

        ::

            sage: d = WordPaths('ab',steps=[(1,2,3),(3,4,5)])._element_classes
            sage: len(d)
            7
            sage: d['FiniteWord_tuple']
            <class 'sage.combinat.words.paths.FiniteWordPath_3d_tuple'>

        ::

            sage: steps = [(1,2,3,4),(3,4,5,6)]
            sage: d = WordPaths('ab',steps=steps)._element_classes
            sage: len(d)
            7
            sage: d['FiniteWord_tuple']
            <class 'sage.combinat.words.paths.FiniteWordPath_all_tuple'>

        ::

            sage: d = WordPaths('ab',steps=[(1,),(3,)])._element_classes
            sage: len(d)
            7
            sage: d['FiniteWord_tuple']
            <class 'sage.combinat.words.paths.FiniteWordPath_all_tuple'>
        """
        dimension = self._vector_space.dimension()
        if dimension == 2:
            return {'FiniteWord_list': FiniteWordPath_2d_list,
            'FiniteWord_str': FiniteWordPath_2d_str,
            'FiniteWord_tuple': FiniteWordPath_2d_tuple,
            #'FiniteWord_cpp_vector': FiniteWordPath_2d_cpp_vector,
            'FiniteWord_callable_with_caching': FiniteWordPath_2d_callable_with_caching,
            'FiniteWord_callable': FiniteWordPath_2d_callable,
            'FiniteWord_iter_with_caching': FiniteWordPath_2d_iter_with_caching,
            'FiniteWord_iter': FiniteWordPath_2d_iter,
            #'InfiniteWord_callable_with_caching': InfiniteWordPath_2d_callable_with_caching,
            #'InfiniteWord_callable': InfiniteWordPath_2d_callable,
            #'InfiniteWord_iter_with_caching': InfiniteWordPath_2d_iter_with_caching,
            #'InfiniteWord_iter': InfiniteWordPath_2d_iter,
            #'Word_iter_with_caching': WordPath_2d_iter_with_caching,
            #'Word_iter': WordPath_2d_iter
            }
        elif dimension == 3:
            return {'FiniteWord_list': FiniteWordPath_3d_list,
            'FiniteWord_str': FiniteWordPath_3d_str,
            'FiniteWord_tuple': FiniteWordPath_3d_tuple,
            #'FiniteWord_cpp_vector': FiniteWordPath_3d_cpp_vector,
            'FiniteWord_callable_with_caching': FiniteWordPath_3d_callable_with_caching,
            'FiniteWord_callable': FiniteWordPath_3d_callable,
            'FiniteWord_iter_with_caching': FiniteWordPath_3d_iter_with_caching,
            'FiniteWord_iter': FiniteWordPath_3d_iter,
            #'InfiniteWord_callable_with_caching': InfiniteWordPath_3d_callable_with_caching,
            #'InfiniteWord_callable': InfiniteWordPath_3d_callable,
            #'InfiniteWord_iter_with_caching': InfiniteWordPath_3d_iter_with_caching,
            #'InfiniteWord_iter': InfiniteWordPath_3d_iter,
            #'Word_iter_with_caching': WordPath_3d_iter_with_caching,
            #'Word_iter': WordPath_3d_iter
            }
        else:
            return {'FiniteWord_list': FiniteWordPath_all_list,
            'FiniteWord_str': FiniteWordPath_all_str,
            'FiniteWord_tuple': FiniteWordPath_all_tuple,
            #'FiniteWord_cpp_vector': FiniteWordPath_all_cpp_vector,
            'FiniteWord_callable_with_caching': FiniteWordPath_all_callable_with_caching,
            'FiniteWord_callable': FiniteWordPath_all_callable,
            'FiniteWord_iter_with_caching': FiniteWordPath_all_iter_with_caching,
            'FiniteWord_iter': FiniteWordPath_all_iter,
            #'InfiniteWord_callable_with_caching': InfiniteWordPath_all_callable_with_caching,
            #'InfiniteWord_callable': InfiniteWordPath_all_callable,
            #'InfiniteWord_iter_with_caching': InfiniteWordPath_all_iter_with_caching,
            #'InfiniteWord_iter': InfiniteWordPath_all_iter,
            #'Word_iter_with_caching': WordPath_all_iter_with_caching,
            #'Word_iter': WordPath_all_iter
            }

    def __repr__(self):
        r"""
        Returns a string representation of self.

        EXAMPLES::

            sage: from sage.combinat.words.paths import WordPaths_all
            sage: d = (vector((1,1)), vector((-1,1)), vector((1,-1)), vector((-1,-1)))
            sage: WordPaths_all('abAB',d).__repr__()
            'Word Paths over 4 steps'
        """
        return "Word Paths over %s steps" % self.size_of_alphabet()

    def letters_to_steps(self):
        r"""
        Returns the dictionary mapping letters to vectors (steps).

        EXAMPLES::

            sage: d = WordPaths('ab').letters_to_steps()
            sage: sorted(d.items())
            [('a', (0, 1)), ('b', (1, 0))]
            sage: d = WordPaths('abcd').letters_to_steps()
            sage: sorted(d.items())
            [('a', (1, 0)), ('b', (0, 1)), ('c', (-1, 0)), ('d', (0, -1))]
            sage: d = WordPaths('abcdef').letters_to_steps()
            sage: sorted(d.items())
            [('a', (1, 0)),
             ('b', (1/2, 1/2*sqrt3)),
             ('c', (-1/2, 1/2*sqrt3)),
             ('d', (-1, 0)),
             ('e', (-1/2, -1/2*sqrt3)),
             ('f', (1/2, -1/2*sqrt3))]
        """
        return self._steps

    def vector_space(self):
        r"""
        Return the vector space over which the steps of the paths are defined.

        EXAMPLES::

            sage: WordPaths('ab',steps='dyck').vector_space()
            Ambient free module of rank 2 over the principal ideal domain Integer Ring
            sage: WordPaths('ab',steps='north_east').vector_space()
            Ambient free module of rank 2 over the principal ideal domain Integer Ring
            sage: WordPaths('abcd',steps='square_grid').vector_space()
            Ambient free module of rank 2 over the principal ideal domain Integer Ring
            sage: WordPaths('abcdef',steps='hexagonal_grid').vector_space()
            Vector space of dimension 2 over Number Field in sqrt3 with defining polynomial x^2 - 3
            sage: WordPaths('abcdef',steps='cube_grid').vector_space()
            Ambient free module of rank 3 over the principal ideal domain Integer Ring
            sage: WordPaths('abcdef',steps='triangle_grid').vector_space()
            Vector space of dimension 2 over Number Field in sqrt3 with defining polynomial x^2 - 3

        """
        return self._vector_space

class WordPaths_square_grid(WordPaths_all):
    r"""
    The combinatorial class of all paths on the square grid.
    """
    def __init__(self, alphabet):
        r"""
        The combinatorial class of all finite paths on the square grid.

        INPUT:

        - ``alphabet`` - ordered alphabet of length 4. The order for the steps
          is : East, North, West, South.

        EXAMPLES::

            sage: from sage.combinat.words.paths import WordPaths_square_grid
            sage: P = WordPaths_square_grid('abAB'); P
            Word Paths on the square grid
            sage: P == loads(dumps(P))
            True

        """
        #Construction of the steps
        d = [(1 ,0), (0,1), (-1,0), (0,-1)]

        #Construction of the class
        super(WordPaths_square_grid, self).__init__(alphabet, steps=d)

    @lazy_attribute
    def _element_classes(self):
        r"""
        Returns a dictionary that gives the class of the elements of self.

        The word may be finite (infinite or of unknown length is not supported
        yet).
        Its data may be str, list, tuple, a callable or an iterable.
        For callable and iterable, the data may be cached.

        TESTS::

            sage: d = WordPaths('abcd')._element_classes
            sage: type(d)
            <type 'dict'>
            sage: len(d)
            7
            sage: d['FiniteWord_tuple']
            <class 'sage.combinat.words.paths.FiniteWordPath_square_grid_tuple'>
        """
        return {'FiniteWord_list': FiniteWordPath_square_grid_list,
        'FiniteWord_str': FiniteWordPath_square_grid_str,
        'FiniteWord_tuple': FiniteWordPath_square_grid_tuple,
        #'FiniteWord_cpp_vector': FiniteWordPath_square_grid_cpp_vector,
        'FiniteWord_callable_with_caching': FiniteWordPath_square_grid_callable_with_caching,
        'FiniteWord_callable': FiniteWordPath_square_grid_callable,
        'FiniteWord_iter_with_caching': FiniteWordPath_square_grid_iter_with_caching,
        'FiniteWord_iter': FiniteWordPath_square_grid_iter,
        #'InfiniteWord_callable_with_caching': InfiniteWordPath_square_grid_callable_with_caching,
        #'InfiniteWord_callable': InfiniteWordPath_square_grid_callable,
        #'InfiniteWord_iter_with_caching': InfiniteWordPath_square_grid_iter_with_caching,
        #'InfiniteWord_iter': InfiniteWordPath_square_grid_iter,
        #'Word_iter_with_caching': WordPath_square_grid_iter_with_caching,
        #'Word_iter': WordPath_square_grid_iter
        }

    def __repr__(self):
        r"""
        EXAMPLES::

            sage: from sage.combinat.words.paths import WordPaths_square_grid
            sage: WordPaths_square_grid('abAB').__repr__()
            'Word Paths on the square grid'
        """
        return "Word Paths on the square grid"

class WordPaths_triangle_grid(WordPaths_all):
    r"""
    The combinatorial class of all paths on the triangle grid.
    """
    def __init__(self, alphabet):
        r"""
        The combinatorial class of all finite paths on the triangle grid.

        INPUT:

        - ``alphabet`` - ordered alphabet of length 6. The order for the steps
          is : Right, Up-Right, Up-Left, Left, Down-Left, Down-Right.

        EXAMPLES::

            sage: from sage.combinat.words.paths import WordPaths_triangle_grid
            sage: P = WordPaths_triangle_grid('abcdef'); P
            Word Paths on the triangle grid
            sage: P == loads(dumps(P))
            True

        """
        K = QuadraticField(3, 'sqrt3')
        sqrt3 = K.gen()

        #Construction of the steps
        d = (vector(K, (1 ,0 )),
             vector(K, (ZZ(1)/ZZ(2), sqrt3/2)),
             vector(K, (ZZ(-1)/ZZ(2), sqrt3/2)),
             vector(K, (-1 , 0 )),
             vector(K, (ZZ(-1)/ZZ(2), -sqrt3/2 )),
             vector(K, (ZZ(1)/ZZ(2), -sqrt3/2 )))

        #Construction of the class
        super(WordPaths_triangle_grid, self).__init__(alphabet, steps=d)

        self._infinite_word_class = None
        self._finite_word_class = FiniteWordPath_triangle_grid

    @lazy_attribute
    def _element_classes(self):
        r"""
        Returns a dictionary that gives the class of the elements of self.

        The word may be finite (infinite or of unknown length is not supported
        yet).
        Its data may be str, list, tuple, a callable or an iterable.
        For callable and iterable, the data may be cached.

        TESTS::

            sage: d = WordPaths('abcdef', steps='triangle')._element_classes
            sage: len(d)
            7
            sage: type(d)
            <type 'dict'>
            sage: d['FiniteWord_tuple']
            <class 'sage.combinat.words.paths.FiniteWordPath_triangle_grid_tuple'>
        """
        return {'FiniteWord_list': FiniteWordPath_triangle_grid_list,
        'FiniteWord_str': FiniteWordPath_triangle_grid_str,
        'FiniteWord_tuple': FiniteWordPath_triangle_grid_tuple,
        #'FiniteWord_cpp_vector': FiniteWordPath_triangle_grid_cpp_vector,
        'FiniteWord_callable_with_caching': FiniteWordPath_triangle_grid_callable_with_caching,
        'FiniteWord_callable': FiniteWordPath_triangle_grid_callable,
        'FiniteWord_iter_with_caching': FiniteWordPath_triangle_grid_iter_with_caching,
        'FiniteWord_iter': FiniteWordPath_triangle_grid_iter,
        #'InfiniteWord_callable_with_caching': InfiniteWordPath_triangle_grid_callable_with_caching,
        #'InfiniteWord_callable': InfiniteWordPath_triangle_grid_callable,
        #'InfiniteWord_iter_with_caching': InfiniteWordPath_triangle_grid_iter_with_caching,
        #'InfiniteWord_iter': InfiniteWordPath_triangle_grid_iter,
        #'Word_iter_with_caching': WordPath_triangle_grid_iter_with_caching,
        #'Word_iter': WordPath_triangle_grid_iter
        }

    def __repr__(self):
        r"""
        EXAMPLES::

            sage: from sage.combinat.words.paths import WordPaths_triangle_grid
            sage: WordPaths_triangle_grid('abcdef').__repr__()
            'Word Paths on the triangle grid'
        """
        return "Word Paths on the triangle grid"

class WordPaths_hexagonal_grid(WordPaths_triangle_grid):
    r"""
    The combinatorial class of all paths on the hexagonal grid.
    """
    def __init__(self, alphabet):
        r"""
        The combinatorial class of all finite paths on the hexagonal grid.

        INPUT:

        - ``alphabet`` - ordered alphabet of length 6. The order for the steps
          is : Right, Up-Right, Up-Left, Left, Down-Left, Down-Right.

        EXAMPLES::

            sage: from sage.combinat.words.paths import WordPaths_hexagonal_grid
            sage: P = WordPaths_hexagonal_grid('abcdef'); P
            Word Paths on the hexagonal grid
            sage: P == loads(dumps(P))
            True

        """
        #Construction of the class
        super(WordPaths_hexagonal_grid, self).__init__(alphabet)

        self._infinite_word_class = None
        self._finite_word_class = FiniteWordPath_hexagonal_grid

    @lazy_attribute
    def _element_classes(self):
        r"""
        Returns a dictionary that gives the class of the elements of self.

        The word may be finite (infinite or of unknown length is not supported
        yet).
        Its data may be str, list, tuple, a callable or an iterable.
        For callable and iterable, the data may be cached.

        TESTS::

            sage: d = WordPaths('abcdef', steps='hexagon')._element_classes
            sage: type(d)
            <type 'dict'>
            sage: len(d)
            7
            sage: d['FiniteWord_tuple']
            <class 'sage.combinat.words.paths.FiniteWordPath_hexagonal_grid_tuple'>
        """
        return {'FiniteWord_list': FiniteWordPath_hexagonal_grid_list,
        'FiniteWord_str': FiniteWordPath_hexagonal_grid_str,
        'FiniteWord_tuple': FiniteWordPath_hexagonal_grid_tuple,
        #'FiniteWord_cpp_vector': FiniteWordPath_hexagonal_grid_cpp_vector,
        'FiniteWord_callable_with_caching': FiniteWordPath_hexagonal_grid_callable_with_caching,
        'FiniteWord_callable': FiniteWordPath_hexagonal_grid_callable,
        'FiniteWord_iter_with_caching': FiniteWordPath_hexagonal_grid_iter_with_caching,
        'FiniteWord_iter': FiniteWordPath_hexagonal_grid_iter,
        #'InfiniteWord_callable_with_caching': InfiniteWordPath_hexagonal_grid_callable_with_caching,
        #'InfiniteWord_callable': InfiniteWordPath_hexagonal_grid_callable,
        #'InfiniteWord_iter_with_caching': InfiniteWordPath_hexagonal_grid_iter_with_caching,
        #'InfiniteWord_iter': InfiniteWordPath_hexagonal_grid_iter,
        #'Word_iter_with_caching': WordPath_hexagonal_grid_iter_with_caching,
        #'Word_iter': WordPath_hexagonal_grid_iter
        }

    def __repr__(self):
        r"""
        EXAMPLES::

            sage: from sage.combinat.words.paths import WordPaths_hexagonal_grid
            sage: WordPaths_hexagonal_grid('abcdef').__repr__()
            'Word Paths on the hexagonal grid'
        """
        return "Word Paths on the hexagonal grid"

class WordPaths_cube_grid(WordPaths_all):
    r"""
    The combinatorial class of all paths on the cube grid.
    """
    def __init__(self, alphabet):
        r"""
        The combinatorial class of all finite paths on the cube grid.

        INPUT:

        - ``alphabet - ordered alphabet of length 6. The order for the steps
          is : e_x, e_y, e_z, -e_x, -e_y, -e_z, where e_v denotes
          the canonical basis.

        EXAMPLES::

            sage: from sage.combinat.words.paths import WordPaths_cube_grid
            sage: P = WordPaths_cube_grid('abcABC'); P
            Word Paths on the cube grid
            sage: P == loads(dumps(P))
            True
        """
        #Construction of the class
        d = [(1,0,0), (0,1,0), (0,0,1), (-1,0,0), (0,-1,0), (0,0,-1)]
        super(WordPaths_cube_grid, self).__init__(alphabet, steps=d)
        self._infinite_word_class = None
        self._finite_word_class = FiniteWordPath_cube_grid

    @lazy_attribute
    def _element_classes(self):
        r"""
        Returns a dictionary that gives the class of the elements of self.

        The word may be finite (infinite or of unknown length is not supported
        yet).
        Its data may be str, list, tuple, a callable or an iterable.
        For callable and iterable, the data may be cached.

        TESTS::

            sage: d = WordPaths('abcdef', steps='cube')._element_classes
            sage: type(d)
            <type 'dict'>
            sage: len(d)
            7
            sage: d['FiniteWord_tuple']
            <class 'sage.combinat.words.paths.FiniteWordPath_cube_grid_tuple'>
        """
        return {'FiniteWord_list': FiniteWordPath_cube_grid_list,
        'FiniteWord_str': FiniteWordPath_cube_grid_str,
        'FiniteWord_tuple': FiniteWordPath_cube_grid_tuple,
        #'FiniteWord_cpp_vector': FiniteWordPath_cube_grid_cpp_vector,
        'FiniteWord_callable_with_caching': FiniteWordPath_cube_grid_callable_with_caching,
        'FiniteWord_callable': FiniteWordPath_cube_grid_callable,
        'FiniteWord_iter_with_caching': FiniteWordPath_cube_grid_iter_with_caching,
        'FiniteWord_iter': FiniteWordPath_cube_grid_iter,
        #'InfiniteWord_callable_with_caching': InfiniteWordPath_cube_grid_callable_with_caching,
        #'InfiniteWord_callable': InfiniteWordPath_cube_grid_callable,
        #'InfiniteWord_iter_with_caching': InfiniteWordPath_cube_grid_iter_with_caching,
        #'InfiniteWord_iter': InfiniteWordPath_cube_grid_iter,
        #'Word_iter_with_caching': WordPath_cube_grid_iter_with_caching,
        #'Word_iter': WordPath_cube_grid_iter
        }

    def __repr__(self):
        r"""
        EXAMPLES::

            sage: from sage.combinat.words.paths import WordPaths_cube_grid
            sage: WordPaths_cube_grid('abcABC').__repr__()
            'Word Paths on the cube grid'
        """
        return "Word Paths on the cube grid"

class WordPaths_dyck(WordPaths_all):
    r"""
    The combinatorial class of all dyck paths.
    """
    def __init__(self, alphabet):
        r"""
        The combinatorial class of all finite Dyck paths.

        INPUT:

        - ``alphabet`` - ordered alphabet of length 2. The order for the steps
          is : (1,1), (1,-1)

        EXAMPLES::

            sage: from sage.combinat.words.paths import WordPaths_dyck
            sage: P = WordPaths_dyck('[]'); P
            Finite Dyck paths
            sage: P == loads(dumps(P))
            True
        """
        #Construction of the class
        d = [(1,1), (1,-1)]
        super(WordPaths_dyck, self).__init__(alphabet, steps=d)

        self._infinite_word_class = None
        self._finite_word_class = FiniteWordPath_dyck

    @lazy_attribute
    def _element_classes(self):
        r"""
        Returns a dictionary that gives the class of the elements of self.

        The word may be finite (infinite or of unknown length is not supported
        yet).
        Its data may be str, list, tuple, a callable or an iterable.
        For callable and iterable, the data may be cached.

        TESTS::

            sage: d = WordPaths('ab', steps='dyck')._element_classes
            sage: type(d)
            <type 'dict'>
            sage: len(d)
            7
            sage: d['FiniteWord_tuple']
            <class 'sage.combinat.words.paths.FiniteWordPath_dyck_tuple'>
        """
        return {'FiniteWord_list': FiniteWordPath_dyck_list,
        'FiniteWord_str': FiniteWordPath_dyck_str,
        'FiniteWord_tuple': FiniteWordPath_dyck_tuple,
        #'FiniteWord_cpp_vector': FiniteWordPath_dyck_cpp_vector,
        'FiniteWord_callable_with_caching': FiniteWordPath_dyck_callable_with_caching,
        'FiniteWord_callable': FiniteWordPath_dyck_callable,
        'FiniteWord_iter_with_caching': FiniteWordPath_dyck_iter_with_caching,
        'FiniteWord_iter': FiniteWordPath_dyck_iter,
        #'InfiniteWord_callable_with_caching': InfiniteWordPath_dyck_callable_with_caching,
        #'InfiniteWord_callable': InfiniteWordPath_dyck_callable,
        #'InfiniteWord_iter_with_caching': InfiniteWordPath_dyck_iter_with_caching,
        #'InfiniteWord_iter': InfiniteWordPath_dyck_iter,
        #'Word_iter_with_caching': WordPath_dyck_iter_with_caching,
        #'Word_iter': WordPath_dyck_iter
        }

    def __repr__(self):
        r"""
        EXAMPLES::

            sage: from sage.combinat.words.paths import WordPaths_dyck
            sage: WordPaths_dyck('()').__repr__()
            'Finite Dyck paths'
        """
        return "Finite Dyck paths"

class WordPaths_north_east(WordPaths_all):
    r"""
    The combinatorial class of all paths using North and East directions.
    """
    def __init__(self, alphabet):
        r"""
        The combinatorial class of all finite paths using only north and east
        steps on the square grid.

        INPUT:

        - ``alphabet`` - ordered alphabet of length 2. The order for the steps
          is North, East

        EXAMPLES::

            sage: from sage.combinat.words.paths import WordPaths_north_east
            sage: P = WordPaths_north_east('ab'); P
            Word Paths in North and East steps
            sage: P == loads(dumps(P))
            True
        """
        #Construction of the class
        d = [(0,1), (1,0)]
        super(WordPaths_north_east, self).__init__(alphabet, steps=d)
        self._infinite_word_class = None
        self._finite_word_class = FiniteWordPath_north_east

    @lazy_attribute
    def _element_classes(self):
        r"""
        Returns a dictionary that gives the class of the elements of self.

        The word may be finite (infinite or of unknown length is not supported
        yet).
        Its data may be str, list, tuple, a callable or an iterable.
        For callable and iterable, the data may be cached.

        TESTS::

            sage: d = WordPaths('ab', steps='NE')._element_classes
            sage: type(d)
            <type 'dict'>
            sage: len(d)
            7
            sage: d['FiniteWord_tuple']
            <class 'sage.combinat.words.paths.FiniteWordPath_north_east_tuple'>
        """
        return {'FiniteWord_list': FiniteWordPath_north_east_list,
        'FiniteWord_str': FiniteWordPath_north_east_str,
        'FiniteWord_tuple': FiniteWordPath_north_east_tuple,
        #'FiniteWord_cpp_vector': FiniteWordPath_north_east_cpp_vector,
        'FiniteWord_callable_with_caching': FiniteWordPath_north_east_callable_with_caching,
        'FiniteWord_callable': FiniteWordPath_north_east_callable,
        'FiniteWord_iter_with_caching': FiniteWordPath_north_east_iter_with_caching,
        'FiniteWord_iter': FiniteWordPath_north_east_iter,
        #'InfiniteWord_callable_with_caching': InfiniteWordPath_north_east_callable_with_caching,
        #'InfiniteWord_callable': InfiniteWordPath_north_east_callable,
        #'InfiniteWord_iter_with_caching': InfiniteWordPath_north_east_iter_with_caching,
        #'InfiniteWord_iter': InfiniteWordPath_north_east_iter,
        #'Word_iter_with_caching': WordPath_north_east_iter_with_caching,
        #'Word_iter': WordPath_north_east_iter
        }

    def __repr__(self):
        r"""
        EXAMPLES::

            sage: from sage.combinat.words.paths import WordPaths_north_east
            sage: WordPaths_north_east('ab').__repr__()
            'Word Paths in North and East steps'
        """
        return "Word Paths in North and East steps"

#######################################################################
#                                                                     #
#                    Abstract word path classes                       #
#                        (all, 2d, 3d, ...)                           #
#                                                                     #
#######################################################################

class FiniteWordPath_all(SageObject):
    def _repr_(self):
        r"""
        Returns a string representation of this path.

        EXAMPLES::

            sage: F = WordPaths('ab',[(1,0,0,0),(0,1,0,0)]); F
            Word Paths over 2 steps
            sage: f = F('ababab')
            sage: f._repr_()
            'Path: ababab'
        """
        return "Path: %s"%self.string_rep()

    def points(self, include_last=True):
        r"""
        Returns an iterator yielding a list of points used to draw the path
        represented by this word.

        INPUT:

        - ``include_last`` - bool (default: True) whether to include the
          last point

        EXAMPLES:

        A simple closed square::

            sage: P = WordPaths('abAB')
            sage: list(P('abAB').points())
            [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]

        A simple closed square without the last point::

            sage: list(P('abAB').points(include_last=False))
            [(0, 0), (1, 0), (1, 1), (0, 1)]

        ::

            sage: list(P('abaB').points())
            [(0, 0), (1, 0), (1, 1), (2, 1), (2, 0)]
        """
        curpt = self.start_point()
        yield curpt
        end = len(self) if include_last else -1
        for l in self[:end]:
            curpt += self.parent().letters_to_steps()[l]
            yield curpt

    def start_point(self):
        r"""
        Returns the starting point of the path.

        EXAMPLES::

            sage: WordPaths('abcdef')('abcdef').start_point()
            (0, 0)
            sage: WordPaths('abcdef', steps='cube_grid')('abcdef').start_point()
            (0, 0, 0)
            sage: P = WordPaths('ab', steps=[(1,0,0,0),(0,1,0,0)])
            sage: P('abbba').start_point()
            (0, 0, 0, 0)
        """
        return self.parent().vector_space()(0)

    @cached_method
    def end_point(self):
        r"""
        Returns the end point of the path.

        EXAMPLES::

            sage: WordPaths('abcdef')('abababab').end_point()
            (6, 2*sqrt3)
            sage: WordPaths('abAB')('abababab').end_point()
            (4, 4)
            sage: P = WordPaths('abcABC', steps='cube_grid')
            sage: P('ababababCC').end_point()
            (4, 4, -2)
            sage: WordPaths('abcdef')('abcdef').end_point()
            (0, 0)
            sage: P = WordPaths('abc', steps=[(1,3,7,9),(-4,1,0,0),(0,32,1,8)])
            sage: P('abcabababacaacccbbcac').end_point()
            (-16, 254, 63, 128)
        """
        last = None
        for pt in self.points():
            last = pt
        return last

    def is_closed(self):
        r"""
        Returns True if the path is closed, i.e. if the origin and the end of
        the path are equal.

        EXAMPLES::

            sage: P = WordPaths('abcd', steps=[(1,0),(0,1),(-1,0),(0,-1)])
            sage: P('abcd').is_closed()
            True
            sage: P('abc').is_closed()
            False
            sage: P().is_closed()
            True
            sage: P('aacacc').is_closed()
            True
        """
        return self.start_point() == self.end_point()

    def is_simple(self):
        r"""
        Returns True if the path is simple, i.e. if all its points are
        distincts.

        If the path is closed, the last point is not considered.

        EXAMPLES::

            sage: P = WordPaths('abcdef',steps='triangle_grid');P
            Word Paths on the triangle grid
            sage: P('abc').is_simple()
            True
            sage: P('abcde').is_simple()
            True
            sage: P('abcdef').is_simple()
            True
            sage: P('ad').is_simple()
            True
            sage: P('aabdee').is_simple()
            False
        """
        n = 0
        s = set()
        include_last = not self.is_closed()
        for p in self.points(include_last=include_last):
            # We need the elements to have a common parent,
            # so we convert the points to immutable vectors.
            v = vector(p)
            v.set_immutable()
            s.add(v)
            n += 1
            if len(s) != n:
                return False
        else:
            return True

    def tikz_trajectory(self):
        r"""
        Returns the trajectory of self as a tikz str.

        EXAMPLES::

            sage: P = WordPaths('abcdef')
            sage: p = P('abcde')
            sage: p.tikz_trajectory()
            '(0.000, 0.000) -- (1.00, 0.000) -- (1.50, 0.866) -- (1.00, 1.73) -- (0.000, 1.73) -- (-0.500, 0.866)'

        """
        from sage.all import n
        f = lambda x: n(x,digits=3)
        l = [str(tuple(map(f, pt))) for pt in self.points()]
        return ' -- '.join(l)

class FiniteWordPath_2d(FiniteWordPath_all):
    def plot(self, pathoptions=dict(rgbcolor='red',thickness=3),
         fill=True, filloptions=dict(rgbcolor='red',alpha=0.2),
         startpoint=True, startoptions=dict(rgbcolor='red',pointsize=100),
         endarrow=True, arrowoptions=dict(rgbcolor='red',arrowsize=20,width=3),
         gridlines=False, gridoptions=dict()):
        r"""
        Returns a 2d Graphics illustrating the path.

        INPUT:

        - ``pathoptions`` - (dict,
          default:dict(rgbcolor='red',thickness=3)), options for the
          path drawing

        - ``fill`` - (boolean, default: True), if fill is True and if
          the path is closed, the inside is colored

        - ``filloptions`` - (dict,
          default:dict(rgbcolor='red',alpha=0.2)), ptions for the
          inside filling

        - ``startpoint`` - (boolean, default: True), draw the start point?

        - ``startoptions`` - (dict,
          default:dict(rgbcolor='red',pointsize=100)) options for the
          start point drawing

        - ``endarrow`` - (boolean, default: True), draw an arrow end at the end?

        - ``arrowoptions`` - (dict,
          default:dict(rgbcolor='red',arrowsize=20, width=3)) options
          for the end point arrow

        - ``gridlines``- (boolean, default: False), show gridlines?

        - ``gridoptions`` - (dict, default: {}), options for the gridlines


        EXAMPLES:

        A non closed path on the square grid::

            sage: P = WordPaths('abAB')
            sage: P('abababAABAB').plot()

        A closed path on the square grid::

            sage: P('abababAABABB').plot()

        A dyck path::

            sage: P = WordPaths('()', steps='dyck')
            sage: P('()()()((()))').plot()

        A path in the triangle grid::

            sage: P = WordPaths('abcdef', steps='triangle_grid')
            sage: P('abcdedededefab').plot()

        A polygon of length 220 that tiles the plane in two ways::

            sage: P = WordPaths('abAB')
            sage: P('aBababAbabaBaBABaBabaBaBABAbABABaBabaBaBABaBababAbabaBaBABaBabaBaBABAbABABaBABAbAbabAbABABaBABAbABABaBabaBaBABAbABABaBABAbAbabAbABAbAbabaBababAbABAbAbabAbABABaBABAbAbabAbABAbAbabaBababAbabaBaBABaBababAbabaBababAbABAbAbab').plot()

        With gridlines::

            sage: P('ababababab').plot(gridlines=True)

        TESTS::

            sage: P = WordPaths('abAB')
            sage: P().plot()
            sage: sum(map(plot,map(P,['a','A','b','B'])))
        """
        G = Graphics()
        pts = list(self.points())

        ####################
        ####################
        #Bug: plot needs float for coordinates
        ####################
        ####################
        pts = [map(RR, x) for x in pts]

        #Inside
        if fill and self.is_closed():
            G += polygon(pts, **filloptions)

        #Startpoint
        if startpoint:
            G += point(pts[0], **startoptions)

        #The path itself
        if endarrow and not self.is_empty():
            G += line(pts[:-1], **pathoptions)
            G += arrow(pts[-2], pts[-1], **arrowoptions)
        else:
            G += line(pts, **pathoptions)

        G.axes(False)
        G.set_aspect_ratio(1)

        #gridlines
        ###############BUG##############
        #Gridlines doesn't work fine.
        #It should be gridlines="integers"
        ###############BUG##############
        if gridlines:
            G = G.show(gridlines=True, **gridoptions)

        return G

    def animate(self):
        r"""
        Returns an animation object illustrating the path growing step by step.

        EXAMPLES::

            sage: P = WordPaths('abAB')
            sage: p = P('aaababbb')
            sage: a = p.animate(); a
            Animation with 9 frames
            sage: show(a)       # optional -- requires convert command
            sage: a.gif(delay=35, iterations=3)       # optional

        ::

            sage: P = WordPaths('abcdef',steps='triangle')
            sage: p =  P('abcdef')
            sage: p.animate()
            Animation with 8 frames

        If the path is closed, the plain polygon is added at the end of the
        animation::

            sage: P = WordPaths('abAB')
            sage: p = P('ababAbABABaB')
            sage: a = p.animate(); a
            Animation with 14 frames

        Another example illustrating a Fibonacci tile::

            sage: w = words.fibonacci_tile(2)
            sage: show(w.animate())      # optional

        The first 4 Fibonacci tiles in an animation::

            sage: a = words.fibonacci_tile(0).animate()
            sage: b = words.fibonacci_tile(1).animate()
            sage: c = words.fibonacci_tile(2).animate()
            sage: d = words.fibonacci_tile(3).animate()
            sage: (a*b*c*d).show()       # optional

        .. note::

            If ImageMagick is not installed, you will get an error
            message like this::

               /usr/local/share/sage/local/bin/sage-native-execute: 8: convert:
               not found

               Error: ImageMagick does not appear to be installed. Saving an
               animation to a GIF file or displaying an animation requires
               ImageMagick, so please install it and try again.

            See www.imagemagick.org, for example.

        """
        from sage.plot.all import line, polygon, animate

        pts = list(self.points())

        ####################
        ####################
        #Bug: plot needs float for coordinates
        ####################
        ####################
        pts = [map(RR, x) for x in pts]

        images = [line(pts[:i]) for i in range(1,len(pts)+1)]

        if self.is_closed():
            images.append(polygon(pts))

        #Get the window of the last image
        last_image = images[-1]
        kwds = {}
        kwds['xmin'] = last_image.xmin()
        kwds['xmax'] = last_image.xmax()
        kwds['ymin'] = last_image.ymin()
        kwds['ymax'] = last_image.ymax()
        kwds['aspect_ratio'] = 1
        kwds['axes'] = False

        return animate(images, **kwds)

    def directive_vector(self, options=dict(rgbcolor='blue')):
        r"""
        Returns an arrow 2d graphics that goes from the start of the path
        to the end.

        INPUT:

        - ``options`` - (dictionary, default: {'rgbcolor': 'blue'} graphic
          options for the arrow

        EXAMPLES::

            sage: P = WordPaths('abcd'); P
            Word Paths on the square grid
            sage: p = P('aaaccaccacacacaccccccbbdd'); p
            Path: aaaccaccacacacaccccccbbdd
            sage: R = p.plot() + p.directive_vector()
            sage: show(R, axes=False, aspect_ratio=1)

        TESTS:

        A closed path::

            sage: P('acbd').directive_vector()
        """
        start = self.start_point()
        end = self.end_point()
        if (start == end) :
            G = point(start, pointsize=10, **options)
        else:
            G = arrow(start, end, **options)
        G.axes(False)
        G.set_aspect_ratio(1)
        return G

    def area(self):
        r"""
        Returns the area of a closed path.

        INPUT:

        - ``self`` - a closed path

        EXAMPLES::

            sage: P = WordPaths('abcd',steps=[(1,1),(-1,1),(-1,-1),(1,-1)])
            sage: p = P('abcd')
            sage: p.area()          #todo: not implemented
            2

        """
        if not self.is_closed():
            raise TypeError, "the path must be closed to compute its area"
        return NotImplemented

class FiniteWordPath_3d(FiniteWordPath_all):
    def plot(self, pathoptions=dict(rgbcolor='red',arrow_head=True,thickness=3),
            startpoint=True, startoptions=dict(rgbcolor='red',size=10)):
        r"""
        INPUT:

        - ``pathoptions`` - (dict, default:dict(rgbcolor='red',arrow_head=True,
          thickness=3)), options for the path drawing

        - ``startpoint`` - (boolean, default: True), draw the start point?

        - ``startoptions`` - (dict, default:dict(rgbcolor='red',size=10))
           options for the start point drawing

        EXAMPLES::

            sage: d = ( vector((1,3,2)), vector((2,-4,5)) )
            sage: P = WordPaths(alphabet='ab', steps=d); P
            Word Paths over 2 steps
            sage: p = P('ababab'); p
            Path: ababab
            sage: p.plot()

            sage: P = WordPaths('abcABC', steps='cube_grid')
            sage: p = P('abcabcAABBC')
            sage: p.plot()

        """
        #The following line seems not to work for 3d
        #G = Graphics()
        #so we draw to start a small almost invisible point instead:
        G = point([self.start_point()], size=1)
        pts = list(self.points())
        if startpoint:
            G += point([pts[0]], **startoptions)
        G += line(pts, **pathoptions)
        return G

#######################################################################
#                                                                     #
#                    Abstract word path classes                       #
#                (square grid, hexagonal grid, etc.)                  #
#                                                                     #
#######################################################################

class FiniteWordPath_square_grid(FiniteWordPath_2d):
    def is_closed(self):
        r"""
        Returns True if self represents a closed path and False otherwise.

        EXAMPLES::

            sage: P = WordPaths('abAB', steps='square_grid')
            sage: P('aA').is_closed()
            True
            sage: P('abAB').is_closed()
            True
            sage: P('ababAABB').is_closed()
            True
            sage: P('aaabbbAABB').is_closed()
            False
            sage: P('ab').is_closed()
            False
        """
        tab = self.parikh_vector()
        return tab[0] == tab[2] and tab[1] == tab[3]

    def area(self):
        r"""
        Returns the area of a closed path.

        INPUT:

        - ``self`` - a closed path

        EXAMPLES::

            sage: P = WordPaths('abAB', steps='square_grid')
            sage: P('abAB').area()
            1
            sage: P('aabbAABB').area()
            4
            sage: P('aabbABAB').area()
            3

        The area of the Fibonacci tiles::

            sage: [words.fibonacci_tile(i).area() for i in range(6)]
            [1, 5, 29, 169, 985, 5741]
            sage: [words.dual_fibonacci_tile(i).area() for i in range(6)]
            [1, 5, 29, 169, 985, 5741]
            sage: sloane_find(_, nresults=1) #optional - internet
            Searching Sloane's online database...
            [[1653,
              'Numbers n such that 2*n^2 - 1 is a square.',
              [1,
               5,
               29,
               169,
               985,
               5741,
               33461,
               195025,
               1136689,
               6625109,
               38613965,
               225058681,
               1311738121,
               7645370045,
               44560482149,
               259717522849,
               1513744654945,
               8822750406821,
               51422757785981,
               299713796309065,
               1746860020068409]]]

        TESTS::

            sage: P = WordPaths('abAB', steps='square_grid')
            sage: P('a').area()
            Traceback (most recent call last):
            ...
            TypeError: the path must be closed to compute its area

        """
        if not self.is_closed():
            raise TypeError, "the path must be closed to compute its area"
        return abs(self._area_vh())

    def _area_vh(path, x=0, y=0):
        r"""
        Returns the area of path, with starting point (x,y) using VH algorithm.

        INPUT:
            x, y -- starting point

        EXAMPLES::

            sage: P = WordPaths('abAB', steps='square_grid')
            sage: P('abAB')._area_vh()
            -1
            sage: P('aabbAABB')._area_vh()
            -4
            sage: P('aabbABAB')._area_vh()
            -3

        REFERENCES:
        Annie Lacasse Memoire.
        """
        area = 0
        a,b,A,B = path.parent().alphabet()

        for move in path:
            if move == b:
                area -= x
                y += 1
            elif move == B:
                area += x
                y -= 1
            elif move == a:
                area += y
                x += 1
            elif move == A:
                area -= y
                x -= 1
        return area/2

    def is_simple(self):
        r"""
        Returns True if the path is simple, i.e. if all its points are
        distincts.

        If the path is closed, the last point is not considered.

        .. note::

            The linear algorithm described in the thesis of Xavier Provençal
            should be implemented here.

        EXAMPLES::

            sage: P = WordPaths('abAB', steps='square_grid')
            sage: P('abab').is_simple()
            True
            sage: P('abAB').is_simple()
            True
            sage: P('abA').is_simple()
            True
            sage: P('aabABB').is_simple()
            False
            sage: P().is_simple()
            True
            sage: P('A').is_simple()
            True
            sage: P('aA').is_simple()
            True
            sage: P('aaA').is_simple()
            False

        REFERENCES:

        - Provençal, X., Combinatoires des mots, geometrie discrete et
          pavages, These de doctorat en Mathematiques, Montreal, UQAM,
          septembre 2008, 115 pages.
        """
        return super(FiniteWordPath_square_grid,self).is_simple()

    def tikz_trajectory(self):
        r"""
        Returns the trajectory of self as a tikz str.

        EXAMPLES::

            sage: f = words.fibonacci_tile(1)
            sage: f.tikz_trajectory()
            '(0, 0) -- (0, -1) -- (-1, -1) -- (-1, -2) -- (0, -2) -- (0, -3) -- (1, -3) -- (1, -2) -- (2, -2) -- (2, -1) -- (1, -1) -- (1, 0) -- (0, 0)'
        """
        return ' -- '.join(map(str,self.points()))

class FiniteWordPath_triangle_grid(FiniteWordPath_2d):
    pass

#TODO: faire une verification du mot pour etre sur hexagonal grid
class FiniteWordPath_hexagonal_grid(FiniteWordPath_triangle_grid):
    def __init__(self, parent, *args, **kwds):
        r"""
        INPUT:

        - ``parent`` - a parent object inheriting from Words_all
          that has the alphabet attribute defined

        - ``*args, **kwds`` - arguments accepted by AbstractWord

        EXAMPLES::

            sage: F = WordPaths('abcdef', steps='hexagon'); F
            Word Paths on the hexagonal grid
            sage: f = F('aaabbbccddef'); f
            Path: aaabbbccddef

        ::

            sage: f == loads(dumps(f))
            True

        """
        super(FiniteWordPath_hexagonal_grid, self).__init__(parent, *args, **kwds)

class FiniteWordPath_cube_grid(FiniteWordPath_3d):
    pass

class FiniteWordPath_north_east(FiniteWordPath_2d):
    pass

class FiniteWordPath_dyck(FiniteWordPath_2d):
    pass

#######################################################################
#                                                                     #
#                    Concrete word path classes                       #
#                                                                     #
#          It would be nice if those were created inline...           #
#       We must ask if Nicolas Thiery was able to convince Sage       #
#       people about this.                                            #
#                                                                     #
#######################################################################

##### Finite paths #####

class FiniteWordPath_all_list(WordDatatype_list, FiniteWordPath_all, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths(['a','b'],[(1,2,0,0),(3,4,0,0)])
        sage: p = P(['a','b','a']);p
        Path: aba
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_all_list'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_all_str(WordDatatype_str, FiniteWordPath_all, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('ab',[(1,2,0,0),(3,4,0,0)])
        sage: p = P('aabbb'); p
        Path: aabbb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_all_str'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_all_tuple(WordDatatype_tuple, FiniteWordPath_all, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('ab',[(1,2,0,0),(3,4,0,0)])
        sage: p = P( ('a','b','b') ); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_all_tuple'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_all_iter_with_caching(WordDatatype_iter_with_caching, FiniteWordPath_all, FiniteWord_class):
    pass

class FiniteWordPath_all_iter(WordDatatype_iter, FiniteWordPath_all, FiniteWord_class):
    pass

class FiniteWordPath_all_callable_with_caching(WordDatatype_callable_with_caching, FiniteWordPath_all, FiniteWord_class):
    pass

class FiniteWordPath_all_callable(WordDatatype_callable, FiniteWordPath_all, FiniteWord_class):
    pass

##### Finite paths on 2d #####

class FiniteWordPath_2d_list(WordDatatype_list, FiniteWordPath_2d, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths(['a','b'],[(1,2),(3,4)])
        sage: p = P(['a','b','a']);p
        Path: aba
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_2d_list'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_2d_str(WordDatatype_str, FiniteWordPath_2d, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths(['a','b'],[(1,2),(3,4)])
        sage: p = P('aba'); p
        Path: aba
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_2d_str'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_2d_tuple(WordDatatype_tuple, FiniteWordPath_2d, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths(['a','b'],[(1,2),(3,4)])
        sage: p = P(('a','b','a'));p
        Path: aba
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_2d_tuple'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_2d_iter_with_caching(WordDatatype_iter_with_caching, FiniteWordPath_2d, FiniteWord_class):
    pass

class FiniteWordPath_2d_iter(WordDatatype_iter, FiniteWordPath_2d, FiniteWord_class):
    pass

class FiniteWordPath_2d_callable_with_caching(WordDatatype_callable_with_caching, FiniteWordPath_2d, FiniteWord_class):
    pass

class FiniteWordPath_2d_callable(WordDatatype_callable, FiniteWordPath_2d, FiniteWord_class):
    pass

##### Finite paths on 3d #####

class FiniteWordPath_3d_list(WordDatatype_list, FiniteWordPath_3d, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths(['a','b'],[(1,2,0),(3,4,0)])
        sage: p = P(['a','b','a']);p
        Path: aba
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_3d_list'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_3d_str(WordDatatype_str, FiniteWordPath_3d, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths(['a','b'],[(1,2,0),(3,4,0)])
        sage: p = P('aba'); p
        Path: aba
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_3d_str'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_3d_tuple(WordDatatype_tuple, FiniteWordPath_3d, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths(['a','b'],[(1,2,0),(3,4,0)])
        sage: p = P(('a','b','a'));p
        Path: aba
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_3d_tuple'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_3d_iter_with_caching(WordDatatype_iter_with_caching, FiniteWordPath_3d, FiniteWord_class):
    pass

class FiniteWordPath_3d_iter(WordDatatype_iter, FiniteWordPath_3d, FiniteWord_class):
    pass

class FiniteWordPath_3d_callable_with_caching(WordDatatype_callable_with_caching, FiniteWordPath_3d, FiniteWord_class):
    pass

class FiniteWordPath_3d_callable(WordDatatype_callable, FiniteWordPath_3d, FiniteWord_class):
    pass

##### Finite paths on square grid #####

class FiniteWordPath_square_grid_list(WordDatatype_list, FiniteWordPath_square_grid, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('abcd', steps='square')
        sage: p = P(['a','b','b']); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_square_grid_list'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_square_grid_str(WordDatatype_str, FiniteWordPath_square_grid, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('abcd', steps='square')
        sage: p = P('abccc'); p
        Path: abccc
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_square_grid_str'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_square_grid_tuple(WordDatatype_tuple, FiniteWordPath_square_grid, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('abcd', steps='square')
        sage: p = P(('a','b','b')); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_square_grid_tuple'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_square_grid_iter_with_caching(WordDatatype_iter_with_caching, FiniteWordPath_square_grid, FiniteWord_class):
    pass

class FiniteWordPath_square_grid_iter(WordDatatype_iter, FiniteWordPath_square_grid, FiniteWord_class):
    pass

class FiniteWordPath_square_grid_callable_with_caching(WordDatatype_callable_with_caching, FiniteWordPath_square_grid, FiniteWord_class):
    pass

class FiniteWordPath_square_grid_callable(WordDatatype_callable, FiniteWordPath_square_grid, FiniteWord_class):
    pass

##### Unknown length paths on square grid (experimental) #####

#class WordPath_square_grid_iter_with_caching(WordDatatype_iter_with_caching, FiniteWordPath_square_grid, Word_class):
#    pass

##### Finite paths on triangle grid #####

class FiniteWordPath_triangle_grid_list(WordDatatype_list, FiniteWordPath_triangle_grid, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('abcdef', steps='triangle')
        sage: p = P(['a','b','b']); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_triangle_grid_list'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_triangle_grid_str(WordDatatype_str, FiniteWordPath_triangle_grid, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('abcdef', steps='triangle')
        sage: p = P('abb'); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_triangle_grid_str'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_triangle_grid_tuple(WordDatatype_tuple, FiniteWordPath_triangle_grid, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('abcdef', steps='triangle')
        sage: p = P(('a','b','b')); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_triangle_grid_tuple'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_triangle_grid_iter_with_caching(WordDatatype_iter_with_caching, FiniteWordPath_triangle_grid, FiniteWord_class):
    pass

class FiniteWordPath_triangle_grid_iter(WordDatatype_iter, FiniteWordPath_triangle_grid, FiniteWord_class):
    pass

class FiniteWordPath_triangle_grid_callable_with_caching(WordDatatype_callable_with_caching, FiniteWordPath_triangle_grid, FiniteWord_class):
    pass

class FiniteWordPath_triangle_grid_callable(WordDatatype_callable, FiniteWordPath_triangle_grid, FiniteWord_class):
    pass

##### Finite paths on hexagonal grid #####

class FiniteWordPath_hexagonal_grid_list(WordDatatype_list, FiniteWordPath_hexagonal_grid, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('abcdef', steps='hexagon')
        sage: p = P(['a','b','b']); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_hexagonal_grid_list'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_hexagonal_grid_str(WordDatatype_str, FiniteWordPath_hexagonal_grid, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('abcdef', steps='hexagon')
        sage: p = P('abb'); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_hexagonal_grid_str'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_hexagonal_grid_tuple(WordDatatype_tuple, FiniteWordPath_hexagonal_grid, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('abcdef', steps='hexagon')
        sage: p = P(('a','b','b')); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_hexagonal_grid_tuple'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_hexagonal_grid_iter_with_caching(WordDatatype_iter_with_caching, FiniteWordPath_hexagonal_grid, FiniteWord_class):
    pass

class FiniteWordPath_hexagonal_grid_iter(WordDatatype_iter, FiniteWordPath_hexagonal_grid, FiniteWord_class):
    pass

class FiniteWordPath_hexagonal_grid_callable_with_caching(WordDatatype_callable_with_caching, FiniteWordPath_hexagonal_grid, FiniteWord_class):
    pass

class FiniteWordPath_hexagonal_grid_callable(WordDatatype_callable, FiniteWordPath_hexagonal_grid, FiniteWord_class):
    pass

##### Finite paths on cube grid #####

class FiniteWordPath_cube_grid_list(WordDatatype_list, FiniteWordPath_cube_grid, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('abcdef', steps='cube')
        sage: p = P(['a','b','b']); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_cube_grid_list'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_cube_grid_str(WordDatatype_str, FiniteWordPath_cube_grid, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('abcdef', steps='cube')
        sage: p = P('abb'); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_cube_grid_str'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_cube_grid_tuple(WordDatatype_tuple, FiniteWordPath_cube_grid, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('abcdef', steps='cube')
        sage: p = P(('a','b','b')); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_cube_grid_tuple'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_cube_grid_iter_with_caching(WordDatatype_iter_with_caching, FiniteWordPath_cube_grid, FiniteWord_class):
    pass

class FiniteWordPath_cube_grid_iter(WordDatatype_iter, FiniteWordPath_cube_grid, FiniteWord_class):
    pass

class FiniteWordPath_cube_grid_callable_with_caching(WordDatatype_callable_with_caching, FiniteWordPath_cube_grid, FiniteWord_class):
    pass

class FiniteWordPath_cube_grid_callable(WordDatatype_callable, FiniteWordPath_cube_grid, FiniteWord_class):
    pass

##### Finite paths on north_east #####

class FiniteWordPath_north_east_list(WordDatatype_list, FiniteWordPath_north_east, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('ab', steps='ne')
        sage: p = P(['a','b','b']); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_north_east_list'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_north_east_str(WordDatatype_str, FiniteWordPath_north_east, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('ab', steps='ne')
        sage: p = P('abb'); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_north_east_str'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_north_east_tuple(WordDatatype_tuple, FiniteWordPath_north_east, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('ab', steps='ne')
        sage: p = P(('a','b','b')); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_north_east_tuple'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_north_east_iter_with_caching(WordDatatype_iter_with_caching, FiniteWordPath_north_east, FiniteWord_class):
    pass

class FiniteWordPath_north_east_iter(WordDatatype_iter, FiniteWordPath_north_east, FiniteWord_class):
    pass

class FiniteWordPath_north_east_callable_with_caching(WordDatatype_callable_with_caching, FiniteWordPath_north_east, FiniteWord_class):
    pass

class FiniteWordPath_north_east_callable(WordDatatype_callable, FiniteWordPath_north_east, FiniteWord_class):
    pass

##### Finite paths on dyck #####

class FiniteWordPath_dyck_list(WordDatatype_list, FiniteWordPath_dyck, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('ab', steps='dyck')
        sage: p = P(['a','b','b']); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_dyck_list'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_dyck_str(WordDatatype_str, FiniteWordPath_dyck, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('ab', steps='dyck')
        sage: p = P('abb'); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_dyck_str'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_dyck_tuple(WordDatatype_tuple, FiniteWordPath_dyck, FiniteWord_class):
    r"""
    TESTS::

        sage: P = WordPaths('ab', steps='dyck')
        sage: p = P(('a','b','b')); p
        Path: abb
        sage: type(p)
        <class 'sage.combinat.words.paths.FiniteWordPath_dyck_tuple'>
        sage: p == loads(dumps(p))
        True
    """
    pass

class FiniteWordPath_dyck_iter_with_caching(WordDatatype_iter_with_caching, FiniteWordPath_dyck, FiniteWord_class):
    pass

class FiniteWordPath_dyck_iter(WordDatatype_iter, FiniteWordPath_dyck, FiniteWord_class):
    pass

class FiniteWordPath_dyck_callable_with_caching(WordDatatype_callable_with_caching, FiniteWordPath_dyck, FiniteWord_class):
    pass

class FiniteWordPath_dyck_callable(WordDatatype_callable, FiniteWordPath_dyck, FiniteWord_class):
    pass
