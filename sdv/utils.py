"""Miscellaneous utility functions."""
import pkg_resources


def display_tables(tables, max_rows=10, datetime_fmt='%Y-%m-%d %H:%M:%S', row=True):
    """Display mutiple tables side by side on a Jupyter Notebook.

    Args:
        tables (dict[str, DataFrame]):
            ``dict`` containing table names and pandas DataFrames.
        max_rows (int):
            Max rows to show per table. Defaults to 10.
        datetime_fmt (str):
            Format with which to display datetime columns.
    """
    # Import here to avoid making IPython a hard dependency
    from IPython.core.display import HTML

    names = []
    data = []
    for name, table in tables.items():
        table = table.copy()
        for column in table.columns:
            column_data = table[column]
            if column_data.dtype.kind == 'M':
                table[column] = column_data.dt.strftime(datetime_fmt)

        names.append('<td style="text-align:left"><b>{}</b></td>'.format(name))
        data.append('<td>{}</td>'.format(table.head(max_rows).to_html(index=False)))

    if row:
        html = '<table><tr>{}</tr><tr>{}</tr></table>'.format(
            ''.join(names),
            ''.join(data),
        )
    else:
        rows = [
            '<tr>{}</tr><tr>{}</tr>'.format(name, table)
            for name, table in zip(names, data)
        ]
        html = '<table>{}</table>'.format(''.join(rows))

    return HTML(html)


def get_package_versions(model=None):
    """Get the package versions for SDV libraries.

    Args:
        model (object or None):
            If model is not None, also store the SDV library versions relevant to this model.
    Returns:
        dict:
            A mapping of library to current version.
    """
    versions = {}
    try:
        versions['sdv'] = pkg_resources.get_distribution('sdv').version
        versions['rdt'] = pkg_resources.get_distribution('rdt').version
    except pkg_resources.ResolutionError:
        pass

    if model is not None:
        if not isinstance(model, type):
            model = model.__class__

        model_name = model.__module__ + model.__name__

        for lib in ['copulas', 'ctgan', 'deepecho']:
            if lib in model_name or ('hma' in model_name and lib == 'copulas'):
                try:
                    versions[lib] = pkg_resources.get_distribution(lib).version
                except pkg_resources.ResolutionError:
                    pass

    return versions


def compare_package_versions(package_versions):
    """Compare the given package versions to the current package versions.

    Args:
        package_versions (dict[str, str]):
            A mapping from library to expected version.
    Returns:
        str:
            A string containing the user warning with the mismatched package versions details.
    """
    warning_str = ('The libraries used to create the model have older versions '
                   'than your current setup. This may cause errors when sampling.')

    if package_versions is None:
        return warning_str

    mismatched_details = ''
    for lib, version in package_versions.items():
        try:
            current_version = pkg_resources.get_distribution(lib).version
        except pkg_resources.ResolutionError:
            current_version = ''

        if current_version != version:
            mismatched_details += (f'\n{lib} used version `{version}`; '
                                   f'current version is `{current_version}`')

    return f'{warning_str}{mismatched_details}' if mismatched_details else None
