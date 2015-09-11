__author__ = "Chi-Jui Wu <cjw21@st-andrews.ac.uk>"

__all__ = ["config", "boxes", "io", "forms", "pageserver", "sockets", "models", "tasks", "defaults", "restful", "parser"]

import threading

import config
import boxes
import io
import forms
import pageserver
import sockets
import models
import tasks
import defaults
import restful
import parser


def run(host, port):
    """
    Run Recompute
    """
    # init()
    config.app.start(host, port)


def init():
    """
    Initialization function for the web app
    """
    io.server_log_info("Creating recomputations directory")
    io.create_recomputations_dir()
    io.create_logs_dir()

    update_base_vms_thread()
    remove_failed_recomputations_thread()
    remove_logs_thread()


def update_base_vms_thread():
    t = threading.Timer(config.time_update_base_vms, update_base_vms_thread)
    t.daemon = True  # exit when ctrl-c is pressed
    t.start()

    io.server_log_info("Updating base vms")
    io.update_base_vagrantboxes()

    io.server_log_info("Refreshing base boxes information")
    config.base_vms_list = io.get_base_vms_list()


def remove_failed_recomputations_thread():
    t = threading.Timer(config.time_clean_up, remove_failed_recomputations_thread)
    t.daemon = True
    t.start()

    io.server_log_info("Removing failed recomputations")
    io.remove_failed_recomputations()


def remove_logs_thread():
    t = threading.Timer(config.time_clean_up, remove_logs_thread)
    t.daemon = True
    t.start()

    io.server_log_info("Removing logs")
    io.remove_logs()
