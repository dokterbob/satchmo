#! /usr/bin/env python

from optparse import OptionParser
import os.path
import sys

__version__ = "0.1"

USAGE = """pybuild [options] filename1 filename2 ..."""

def posplit(fname, rules):
    sections = make_sections(fname)
    rules.set_header(sections[0])
    rules.set_pofile(fname)
    print "SECTIONS: %s" % fname
    ix = 0
    for section in sections[1:]:
        section.apply_rules(rules)
        section.do_copy()
        ix += 1
        #print ix
    
def make_sections(fname):
    sections = []
    f = open(fname, 'r')
    section=Section()
    for line in f.xreadlines():
        if line and line.endswith("\n"):
            line = line[:-1]
        elif line and (line.endswith("\r\n") or line.endswith("\n\r")):
            line = line[:-2]
            
        if not line:
            sections.append(section)
            section = Section()
        else:
            section.add(line)
            
    return sections

class RuleSet(object):
    
    def __init__(self, fname):
        self.rules = []
        self.fname = fname
        self.parse_rules()
        self.files = {}
        
    def parse_rules(self):
        """Parse a rules file which tells where to put target sections

        The rules file is formatted like:
        slug=[option:]dest

        Where:
        - slug is the beginning part of the filename in the po file.
        - dest is the destination name

        For example:
        accounts=apps/satchmo_store/accounts
        giftcertificate=apps/payment/modules/giftcertificate
        local_settings-customize.py=nostrip:projects/template/
        """
        f = open(self.fname, 'r')
        for line in f.xreadlines():
            if line and line.endswith("\n"):
                line = line[:-1]
            if line and not line.startswith("#"):
                self.add(Rule(line))

    def add(self, rule):
        rule.parent = self
        self.rules.append(rule)
    
    def match_rule(self, target):
        decision = None
        for rule in self.rules:
            if rule.applies_to(target):
                decision = rule
                break
        
        return decision
        
    def open_pofile(self, dest):
        if not dest in self.files:
            #print "making: %s" % dest
            fname = os.path.join(dest, self.pofile)
            d, n = os.path.split(fname)
            if not os.path.exists(d):
                print "Making directory: %s" % d
                os.makedirs(d)
            print "opening: %s" % fname
            f = open(fname, 'w')
            f.write("\n".join(self.header.lines))
            f.write("\n\n")
            self.files[dest] = f
        else:
            pass
            #print "reusing: %s" % dest
        
        return self.files[dest]

    def set_header(self, header):
        self.header = header
        
    def set_pofile(self, fname):
        self.pofile = fname
        
class Rule(object):
    def __init__(self, line):
        try:
            k, v = line.split('=')
        except:
            print "error: '%s'" % line
            raise
        opt = "STRIP"
        if v.find(':') > -1:
            opt, v = v.split(':')
                
        self.parent = None
        self.key = k
        self.option = opt
        self.dest = v

    def applies_to(self, target):
        return target.startswith(self.key)

    def apply(self, target):
        if self.option == "IGNORE":
            return ""
            
        if self.option == "STRIP":
            if target.startswith(self.key):
                target = target[len(self.key):]
        
        return target
        
    def do_copy(self, targets, lines):
        if not self.option=='IGNORE':
            f = self.parent.open_pofile(self.dest)
            targets = ["#: %s" % self.apply(tgt) for tgt in targets]
            f.write("\n".join(targets))
            f.write("\n")
            f.write("\n".join(lines))
            f.write("\n\n")

    def __str__(self):
        return("Rule: %s=(%s) %s" % (self.key, self.option, self.dest))

class Section(object):
    
    def __init__(self):
        self.targets = []
        self.decisions = {}
        self.lines = []
        
    def add(self, line):
        if line.startswith("#: "):
            self.targets.append(line[3:])
        else:
            self.lines.append(line)
            
    def apply_rules(self, rules):
        for target in self.targets:
            decision = rules.match_rule(target)
            
            if decision:
                if decision in self.decisions:
                    self.decisions[decision].append(target)
                else:
                    self.decisions[decision] = [target]
            else:
                print "WARNING, no decision made for target: '%s'" % target
                sys.exit(3)
            
    def do_copy(self):
        for rule, targets in self.decisions.items():
            rule.do_copy(targets, self.lines)

    def __unicode__(self):
        out = ['TARGETS: ',]
        out.extend(self.targets)
        out.append('DECISIONS: ')
        for k, v in self.decisions.items():
            out.append('%s = %s' % (k.key, ", ".join(v)))

        out.append('LINES:')
        out.extend(self.lines)
        return "\n".join(out)


def main(args):
    parser = OptionParser(USAGE, version = __version__)
    
    parser.add_option('-c','--conf', dest='conf',
                      default='posplit.rules', 
                      help="the posplit rules file")
    
    opts, fnames = parser.parse_args(args)
    
    if not fnames:
        print "Need at least one filename"
        print USAGE
        sys.exit(2)
        
    if not opts.conf:
        print "Need a config file"
        print USAGE
        sys.exit(2)
        
    rules = RuleSet(opts.conf)
    
    for fname in fnames:
        posplit(fname, rules)
    
if __name__=='__main__':
    main(sys.argv[1:])