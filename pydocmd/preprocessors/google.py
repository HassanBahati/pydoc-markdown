import re


class Preprocessor:
    """
    This class implements the preprocessor for Google style.
    """
    _param_res = [
        re.compile(r'^(?P<param>\S+): (?P<desc>.+)$'),
        re.compile(r'^(?P<param>\S+)\s(?P<type>\S+): (?P<desc>.+)$'),
        re.compile(r'^(?P<param>\S+)\s+-- (?P<desc>.+)$'),
        re.compile(
            r'^(?P<param>\S+)\s+\{\[(?P<type>\S+)\]\}\s+-- (?P<desc>.+)$'),
        re.compile(
            r'^(?P<param>\S+)\s+\{(?P<type>\S+)\}\s+-- (?P<desc>.+)$'),
    ]

    keywords_map = {
        'Args:': 'Arguments',
        'Arguments:': 'Arguments',
        'Keyword Arguments:': 'Arguments',
        'Returns:': 'Returns',
        'Raises:': 'Raises',
    }

    def __init__(self, config=None):
        self.config = config

    def preprocess_section(self, section):
        """
        Preprocessors a given section into it's components.
        """
        lines = []
        in_codeblock = False
        keyword = None
        components = {}

        for line in section.content.split('\n'):
            line = line.strip()

            if line.startswith("```"):
                in_codeblock = not in_codeblock

            if in_codeblock:
                lines.append(line)
                continue

            if line in self.keywords_map:
                keyword = self.keywords_map[line]
                continue

            if keyword is None:
                lines.append(line)
                continue

            if keyword not in components:
                components[keyword] = []

            for param_re in self._param_res:
                param_match = param_re.match(line)
                if param_match:
                    if 'type' in param_match.groupdict():
                        components[keyword].append(
                            '- `{param}` _{type}_ - {desc}'.format(**param_match.groupdict()))
                    else:
                        components[keyword].append(
                            '- `{param}` - {desc}'.format(**param_match.groupdict()))
                    break

            if not param_match:
                components[keyword].append(f'  {line}')

        for key in components:
            self._append_section(lines, key, components)

        section.content = '\n'.join(lines)

    @staticmethod
    def _append_section(lines, key, sections):
        section = sections.get(key)
        if not section:
            return

        if lines and lines[-1]:
            lines.append('')

        # add an extra line because of markdown syntax
        lines.extend(['**{}**:'.format(key), ''])
        lines.extend(section)
