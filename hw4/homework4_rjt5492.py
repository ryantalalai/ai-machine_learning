############################################################
# CMPSC 442: Logic
############################################################

student_name = "Ryan Joseph Talalai"

############################################################
# Imports
############################################################

# Include your imports here, if any are used.
from itertools import product


############################################################
# Section 1: Propositional Logic
############################################################

class Expr(object):
    def __hash__(self):
        return hash((type(self).__name__, self.hashable))

class Atom(Expr):
    def __init__(self, name):
        self.name = name
        self.hashable = name

    def __hash__(self):
        return hash((type(self).__name__, self.hashable))    

    def __eq__(self, other):
        return type(self) == type(other) and self.hashable == other.hashable

    def __repr__(self):
        return f"Atom({self.name})"
    
    def __iter__(self):
        yield self

    def atom_names(self):
        return {self.name}

    def evaluate(self, assignment):
        return assignment.get(self.name, False)

    def to_cnf(self):
        return self

class Not(Expr):
    def __init__(self, arg):
        self.arg = arg
        self.hashable = arg

    def __hash__(self):
        return hash((type(self).__name__, self.hashable))    

    def __eq__(self, other):
        return type(self) == type(other) and self.hashable == other.hashable

    def __repr__(self):
        return f"Not({self.arg})"
    
    def __iter__(self):
        yield self

    def atom_names(self):
        return self.arg.atom_names()

    def evaluate(self, assignment):
        return not self.arg.evaluate(assignment)

    def to_cnf(self):
        cnf = self.arg.to_cnf()

        if isinstance(cnf, Not):
            return cnf.arg
        elif isinstance(cnf, And):
            return Or(*[Not(c).to_cnf() for c in cnf.conjuncts])
        elif isinstance(cnf, Or):
            return And(*[Not(c).to_cnf() for c in cnf.disjuncts])
        
        return Not(cnf)
        
class And(Expr):
    def __init__(self, *conjuncts):
        self.conjuncts = frozenset(conjuncts)
        self.hashable = self.conjuncts

    def __hash__(self):
        return hash((type(self).__name__, self.hashable))    

    def __eq__(self, other):
        return type(self) == type(other) and self.hashable == other.hashable

    def __repr__(self):
        temp = ",".join(repr(i) for i in self.conjuncts)
        return f"And({temp})"
    
    def __iter__(self):
        for i in self.conjuncts: 
            yield i

    def atom_names(self):
        return set().union(*(i.atom_names() for i in self.conjuncts))

    def evaluate(self, assignment):
        return all(i.evaluate(assignment) for i in self.conjuncts)

    def to_cnf(self):
        cnf_conjuncts = [i.to_cnf() for i in self.conjuncts]
        final = []
        for conjunct in cnf_conjuncts:
            if isinstance(conjunct, And):
                final.extend(conjunct.conjuncts)
            else:
                final.append(conjunct)
        return And(*final)

class Or(Expr):
    def __init__(self, *disjuncts):
        self.disjuncts = frozenset(disjuncts)
        self.hashable = self.disjuncts

    def __hash__(self):
        return hash((type(self).__name__, self.hashable))    

    def __eq__(self, other):
        return type(self) == type(other) and self.hashable == other.hashable

    def __repr__(self):
        disjuncts_repr = ",".join(repr(i) for i in self.disjuncts)
        return f"Or({disjuncts_repr})"
    
    def __iter__(self):
        for i in self.disjuncts:
            yield i 

    def atom_names(self):
        return set().union(*(i.atom_names() for i in self.disjuncts))

    def evaluate(self, assignment):
        return any(i.evaluate(assignment) for i in self.disjuncts)

    def to_cnf(self):
        cnf_elements = [element.to_cnf() for element in self.disjuncts]
        conjunctions, disjunctions = [], []
        for element in cnf_elements:
            if isinstance(element, And):
                conjunctions.append(element)
            elif isinstance(element, Or):
                disjunctions.extend(element.disjuncts)
            else:
                disjunctions.append(element)
        if conjunctions:
            combined = self._helper_conj(conjunctions)
            return And(*[self._helper_disj(conj, disjunctions) for conj in combined.conjuncts])
        else:
            return Or(*disjunctions)

    def _helper_conj(self, conjunctions):
        combined = conjunctions[0]
        for next_conj in conjunctions[1:]:
            new_conjuncts = []
            for conj1 in combined.conjuncts:
                for conj2 in next_conj.conjuncts:
                    disjuncts_list = frozenset(self._helper_sing(conj1)).union(self._helper_sing(conj2))
                    new_conjuncts.append(Or(*disjuncts_list))
            combined = And(*new_conjuncts)
        return combined

    def _helper_disj(self, conj, disjunctions):
        disjuncts_combined = frozenset(self._helper_sing(conj)).union(disjunctions)
        return Or(*disjuncts_combined)

    def _helper_sing(self, element):
        return element.disjuncts if isinstance(element, Or) else frozenset([element])

class Implies(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.hashable = (left, right)

    def __hash__(self):
        return hash((type(self).__name__, self.hashable))    

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.left == other.left and self.right == other.right

    def __repr__(self):
        return f"Implies({repr(self.left)},{repr(self.right)})"

    def atom_names(self):
        return self.left.atom_names().union(self.right.atom_names())

    def evaluate(self, assignment):
        return not self.left.evaluate(assignment) or self.right.evaluate(assignment)

    def to_cnf(self):
        return Or(Not(self.left), self.right).to_cnf()

class Iff(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.hashable = (left, right)

    def __hash__(self):
        return hash((type(self).__name__, self.hashable))

    def __eq__(self, other):
        if type(self) is type(other):
            return (self.left == other.left and self.right == other.right) or (self.left == other.right and self.right == other.left)
        else:
            return False

    def __repr__(self):
        return f"Iff({repr(self.left)},{repr(self.right)})"

    def atom_names(self):
        return self.left.atom_names().union(self.right.atom_names())

    def evaluate(self, assignment):
        return self.left.evaluate(assignment) == self.right.evaluate(assignment)

    def to_cnf(self):
        return And(Or(Not(self.left), self.right), Or(Not(self.right), self.left)).to_cnf()

def satisfying_assignments(expr):
    atom_names = list(expr.atom_names())
    for values in product([False, True], repeat=len(atom_names)):
        assignment = {atom: value for atom, value in zip(atom_names, values)}
        if expr.evaluate(assignment):
            yield assignment

class KnowledgeBase(object):
    def __init__(self):
        self.all_facts = set()

    def get_facts(self):
        return self.all_facts

    def tell(self, proposition):
        cnf_proposition = proposition.to_cnf()
        if isinstance(cnf_proposition, And):
            self.all_facts.update(cnf_proposition.conjuncts)
        else:
            self.all_facts.add(cnf_proposition)

    def ask(self, expr):
        query_negation = Not(expr)
        combined_assumption = And(*self.all_facts, query_negation).to_cnf()
        try:
            next(satisfying_assignments(combined_assumption))
            return False
        except:
            return True



############################################################
# Section 2: Logic Puzzles
############################################################

# Puzzle 1

# Populate the knowledge base using statements of the form kb1.tell(...)
kb1 = KnowledgeBase()

mythical = Atom("mythical")
mortal = Atom("mortal")
mammal = Atom("mammal")
horned = Atom("horned")
magical = Atom("magical")

kb1.tell(Implies(mythical, Not(mortal)))
kb1.tell(Implies(Not(mythical), And(mortal, mammal)))
kb1.tell(Implies(Or(Not(mortal), mammal), horned))
kb1.tell(Implies(horned, magical))

# Write an Expr for each query that should be asked of the knowledge base
mythical_query = mythical
magical_query = magical
horned_query = horned

# Record your answers as True or False; if you wish to use the above queries,
# they should not be run when this file is loaded
is_mythical = False
is_magical = True
is_horned = True

# Puzzle 2

# Write an Expr of the form And(...) encoding the constraints
a = Atom("a")
j = Atom("j")
m = Atom("m")

party_constraints = And(Implies(Or(m, a), j), Implies(Not(m), a), Implies(a, Not(j)))

# Compute a list of the valid attendance scenarios using a call to
# satisfying_assignments(expr)
valid_scenarios = list(satisfying_assignments(party_constraints))

# Write your answer to the question in the assignment
puzzle_2_question = """
The Valid Solution is:
Ann: Does not attend
John: Attends
Mary: Attends
"""

# Puzzle 3

# Populate the knowledge base using statements of the form kb3.tell(...)

kb3 = KnowledgeBase()

p1 = Atom("p1")
e1 = Atom("e1")
p2 = Atom("p2")
e2 = Atom("e2")
s1 = Atom("s1")
s2 = Atom("s2")

kb3.tell(Implies(s1, And(p1, e2)))
kb3.tell(Implies(s2, And(Or(p1, p2), Or(e1, e2))))

kb3.tell(Implies(p1, Not(e1)))
kb3.tell(Implies(p2, Not(e2)))
kb3.tell(Implies(e1, Not(p1)))
kb3.tell(Implies(e2, Not(p2)))

kb3.tell(And(And(Implies(s1, Not(s2)), Implies(s2, Not(s1))), Or(s1, s2)))



# Write your answer to the question in the assignment; the queries you make
# should not be run when this file is loaded
puzzle_3_question = """
Room 1: prize
Room 2: empty
"""

# Puzzle 4

# Populate the knowledge base using statements of the form kb4.tell(...)

kb4 = KnowledgeBase()

ia = Atom("ia")
ib = Atom("ib")
ic = Atom("ic")
ka = Atom("ka")
kb = Atom("kb")
kc = Atom("kc")

kb4.tell(Implies(ia, And(kb, Not(kc))))
kb4.tell(kb)
kb4.tell(Implies(ic, And(ka, kb)))


# Uncomment the line corresponding to the guilty suspect
# guilty_suspect = "Adams"
guilty_suspect = "Brown"
# guilty_suspect = "Clark"

# Describe the queries you made to ascertain your findings
puzzle_4_question = """
Brown is the guilty suspect
"""
