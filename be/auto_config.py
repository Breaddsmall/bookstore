from be.model import db_conn
import be.auto_job

class Config(object):
    JOBS = [

        {
            'id': 'job1',
            'func': be.auto_job.auto_cancel,  # 方法名
            'trigger': 'interval',  # interval表示循环任务
            'seconds': 2,
        },

        {
            'id': 'job2',
            'func': be.auto_job.auto_receive,  # 方法名
            'trigger': 'interval',  # interval表示循环任务
            'seconds': 2,
        }
    ]

