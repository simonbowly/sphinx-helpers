import nox


@nox.session()
@nox.parametrize("python", ["3.11", "3.12", "3.13"])
@nox.parametrize("sphinx", ["7.0", "7.1", "7.2", "7.3", "7.4", "8.0", "8.1", "8.2"])
def tests(session, sphinx):
    session.install(f"sphinx[test]=={sphinx}.*", ".")
    session.run("pip", "list")
    session.run("pytest")
