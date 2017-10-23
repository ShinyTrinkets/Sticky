
from .util import locate_file, hash_text, increment_rev
from .util import split_py_source_file, extract_head_info
from .constant import MARKER_A, MARKER_Z, HASH_LEN


class Source:
    """
    This class represents a source file text, that must be `ickyfied`
    """
    def __init__(self, fname=None, text='', **options):
        if text:
            self.fname = fname
            self.head, self.tail = split_py_source_file(text)
        else:
            if not fname:
                fname = locate_file()
                if not fname and not text:
                    raise Exception('Cannot locate file to ickyfy')
            self.fname = fname
            text = open(fname, 'r').read()
            self.head, self.tail = split_py_source_file(text)
        # Save extra options
        self.marker_a = options.get('marker_a', MARKER_A)
        self.marker_z = options.get('marker_z', MARKER_Z)
        self.hash_len = options.get('hash_len', HASH_LEN)

    def inject_sticky_info(self):
        """
        Merge head and tail with the old info.
        """
        head, old_info = extract_head_info(self.head, self.marker_a, self.marker_z)
        rev = old_info.get('rev', 'v0')
        hash = hash_text(self.tail, self.hash_len)
        if hash != old_info.get('hash'):
            rev = increment_rev(rev)
        info = {
            'rev': rev,
            'hash': hash,
            'start': self.marker_a,
            'finis': self.marker_z,
        }
        icky = '\n#{start} rev: {rev} {finis}\n' \
               '#{start} hash: {hash} {finis}\n\n'.format(**info)
        return head.rstrip() + icky + self.tail

    def save_header(self):
        """
        Save header, overwriting the source file.
        """
        with open(self.fname, 'w') as out_file:
            out_file.write(self.inject_sticky_info())