from docutils.core import publish_parts
from markdownify import markdownify
from numpydoc.docscrape import NumpyDocString

def docstr_to_html(docstr):
    """
    Converts a docstring into HTML format.
    
    Parameters
    ----------
    docstr : str
        Docstring to convert into HTML.
    
    Returns
    -------
    str
        HTML formatted docstring.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        from msdss_models_api.models import Model
        from msdss_models_api.tools import *
        from pprint import pprint

        docstr = ''.join(get_npdoc(Model)['Extended Summary'])
        html = docstr_to_html(docstr)
        pprint(html)
    """
    out = publish_parts(
        source=docstr,
        writer_name='html',
        settings_overrides={'report_level': 4})['html_body']
    return out

def get_md_doc(obj):
    """
    Converts a Python objects numpy style docstring into markdown for the summary, extended summary, and parameters headings.
    
    Parameters
    ----------
    obj : any or str
        A python object with numpy style docstring. If ``str``, then it will assume that the str will be the docstring.
    
    Returns
    -------
    str
        Markdown formatted docstring for the summary, extended summary, and parameters headings.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        from msdss_models_api.models import Model
        from msdss_models_api.tools import *
        from pprint import pprint

        model_doc = get_md_doc(Model)
        pprint(model_doc)
    """
    
    # (get_model_doc_numpy) Get doc and convert to numpy doc str
    npdoc = get_npdoc(obj)

    # (get_model_doc_summary) Get npdoc summary and convert to html
    summary = '\n\n'.join([''.join(npdoc[k]) for k in ['Summary', 'Extended Summary']])
    summary = docstr_to_html(summary)

    # (get_model_doc_params) Get npdoc parameters and convert to html
    parameters = '\n'.join(['* ' + k.name + ': ' + ''.join(k.desc) for k in npdoc['Parameters']])
    parameters = docstr_to_html(parameters)
    parameters = '<h2>Parameters</h2>' + parameters
    
    # (get_model_doc_out) Combine html and convert to md docs
    out = summary + '<br>' + parameters
    out = html_to_md(out)
    return out

def get_npdoc(obj):
    """
    Parses a numpy style docstring from a Python object.
    
    Parameters
    ----------
    obj : any or str
        A python object with numpy style docstring. If ``str``, then it will assume that the str will be the docstring.
    
    Returns
    -------
    :class:`numpydoc:numpydoc.docscrape.NumpyDocString`
        A parsed numpy docstring object.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        from msdss_models_api.models import Model
        from msdss_models_api.tools import *
        from pprint import pprint

        docstr = ''.join(get_npdoc(Model)['Extended Summary'])
        pprint(docstr)
    """
    out = NumpyDocString(obj) if isinstance(obj, str) else NumpyDocString(obj.__doc__)
    return out

def html_to_md(html):
    """
    Converts HTML into markdown format.
    
    Parameters
    ----------
    html : str
        HTML to convert to markdown.
    
    Returns
    -------
    str
        markdown formatted from HTML.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        from msdss_models_api.models import Model
        from msdss_models_api.tools import *
        from pprint import pprint

        docstr = ''.join(get_npdoc(Model)['Extended Summary'])
        html = docstr_to_html(docstr)
        md = html_to_md(html)
        pprint(md)
    """
    out = markdownify(html)
    return out