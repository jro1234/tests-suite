import os
import subprocess
import shlex

# TODO replace path insert formatting with os.path.join
class MongoInstance(object):
    """A simple interface to mongod instance
    TODO describe it!
    """
    def __init__(self, dbpath, dbport=27017):
        super(MongoInstance, self).__init__()

        assert self.discover_mongod_command()
        assert isinstance(dbpath, str) # TODO check is path-like, parent dir exists
        #assert isinstance(dbport, validport) # TODO isint and betwen X and Y

        self._dblog_file = None
        self.dbpath = dbpath
        self.dbport = dbport

    def discover_mongod_command(self):
        proc = subprocess.Popen(
            shlex.split("command -v mongod"),
            stdout=subprocess.PIPE, stderr=subprocess.IGNORE
        )

        out = proc.stdout.read()
        retval = proc.wait()

        if out: return True
        else:   return False

    @property
    def pid(self):
        return self.mongo_proc.pid

    @property
    def mongo_proc(self):
        return self._mongo_proc

    @property
    def dblogfile(self):
        return self._dblog_file

    def open_mongodb(self, remove_socket=False,
            remove_locks=False, create_folder=False):

        if create_folder:
            try:
                os.mkdir(self.dbpath)
                os.mkdir('{}/socket'.format(self.dbpath))
                os.mkdir('{}/db'.format(self.dbpath))

            except OSError:
                pass

        if remove_socket:
            self._remove_socket_file()

        if remove_locks:
            self._remove_lock_files()

        self._write_config_file()

        self._dblog_file = open(
            "{0}/db.log".format(self.dbpath), 'w')

        #if command -v numactl: launcher -= "numactl --interleave=all"
        launcher = "mongod --dbpath {0}/db --config {0}/db.cfg"

        self._mongo_proc = subprocess.Popen(
            shlex.split(launcher.format(self.dbpath)),
            stdout=self._dblog_file,
            stderr=self._dblog_file,
        )

    def stop_mongodb(self):

        self._mongo_proc.kill()
        self._mongo_proc.wait()
        self._dblog_file.close()
        self._remove_socket_file()
        self._remove_lock_files()

    def _remove_lock_files(self):

        mongo_lock_file = '{0}/db/mongod.lock'.format(self.dbpath)
        wt_lock_file = '{0}/db/WiredTiger.lock'.format(self.dbpath)

        if os.path.exists(mongo_lock_file):
            os.remove(mongo_lock_file)

        if os.path.exists(wt_lock_file):
            os.remove(wt_lock_file)

    def _remove_socket_file(self):

        socket_file = '{0}/socket/mongodb-{1}.sock'\
            ''.format(self.dbpath, self.dbport)

        if os.path.exists(socket_file):
            os.remove(socket_file)

    def _write_config_file(self):

        config_string = ""\
            "net:\n"\
            "   unixDomainSocket:\n"\
            "      pathPrefix: {0}/socket\n"\
            "   bindIp: localhost\n"\
            "   port:   {1}\n"\
            "".format(self.dbpath, self.dbport)
            
        config_file = "{0}/db.cfg".format(self.dbpath)

        with open(config_file,"w") as cfg:
            cfg.write(config_string)


class SessionMover(object):
    """Use this object to roll out new locations for session log files, and
    move between session locations and a starting location. Iterate to create
    new session IDs. Call `use_current` method to create folders for the
    current session and move to this working directory, then `go_back` to
    change back to the starting directory.
    
    Methods
    -------
    __init__ :: init with base path, scans for existing sessions
    use_current :: use the current session ID, ie create and go to this session folder
    use_next :: create and use the next session ID
    go_back :: move back to base path
    
    """
    _base = None
    _prefix = 'sessions'
    _first = 0
    _capture = '.log'

    def __init__(self, path):
        super(SessionMover, self).__init__()

        self._base = path
        self._path = os.path.join(path, SessionMover._prefix)
        self._currentID = None
        self._init_sessionID()

    def _init_sessionID(self):
        if not os.path.exists(self._path):
            os.mkdir(self._path)

        existing_sessions = os.listdir(self._path)
        newest = SessionMover._first

        if existing_sessions:
            for d in existing_sessions:
                try:
                    this = int(d)
                    if this > newest:
                        newest = this

                except ValueError:
                    pass

        self._currentID = newest + 1

    def capture_fwd_logs(self):
        return filter(
            lambda f: f.endswith(SessionMover._capture),
            os.listdir(self._base)
        )

    def _incr_currentID(self):
        self._currentID += 1

    def use_next(self):
        next(self)
        self.use_current()

    def use_current(self):
        os.mkdir(self.current)
        os.chdir(self.current)

    def go_back(self, capture=False):
        os.chdir(self._base)
        if capture:
            [
             os.rename(f, os.path.join(self.current, f))
             for f in self.capture_fwd_logs()
            ]

    @property
    def currentID(self):
        return "{:04}".format(self._currentID)

    @property
    def current(self):
        return os.path.join(self._path, self.currentID)

    def __iter__(self):
        return self

    def next(self):
        return self.__next__()

    def __next__(self):

        self._incr_currentID()

        if self._currentID > 9999:
            raise StopIteration

        return self.current
