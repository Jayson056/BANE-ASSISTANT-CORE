# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
import platform
import psutil
import subprocess
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from telegram_interface.auth import is_authorized

logger = logging.getLogger(__name__)

def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a detailed system report in the user's requested format."""
    user = update.effective_user
    if not user or not is_authorized(user.id):
        return

    try:
        # 1. Header & Time
        gen_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 2. System Info
        uname = platform.uname()
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.fromtimestamp(boot_time_timestamp)
        uptime = datetime.now() - bt
        uptime_str = str(uptime).split('.')[0]
        
        # 3. CPU Usage
        cpufreq = psutil.cpu_freq()
        cpu_load = psutil.cpu_percent(interval=None)
        
        # 4. Memory
        svmem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # 5. Disk Usage
        partitions = psutil.disk_partitions()
        disk_info = ""
        for partition in partitions:
            if partition.mountpoint in ['/', '/boot/efi'] or '/media/' in partition.mountpoint:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info += f"   Used: {get_size(usage.used)} / {get_size(usage.total)} ({usage.percent}%) {partition.mountpoint} ({partition.fstype})\n"
                except (PermissionError, OSError):
                    continue

        # 6. Top Processes (By Memory)
        top_procs = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                top_procs.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        top_procs = sorted(top_procs, key=lambda x: x['memory_percent'], reverse=True)[:4]
        proc_info = ""
        for p in top_procs:
            proc_info += f" {p['name']} (PID: {p['pid']}) - {p['memory_percent']:.2f}%\n"

        # Constructing the exact format requested
        report = (
            f"ℹ️ *UPDATE*\n\n"
            f"🖥️ **SYSTEM STATUS REPORT**\n\n"
            f"📅 Generated: `{gen_time}`\n\n"
            f"💻 **SYSTEM INFO**\n"
            f"```\n"
            f"OS: {uname.system} {uname.release}\n"
            f"Node: {uname.node}\n"
            f"Machine: {uname.machine}\n"
            f"Uptime: {uptime_str}\n"
            f"```\n"
            f"⚙️ **CPU USAGE**\n"
            f"```\n"
            f"Cores: {psutil.cpu_count(logical=False)}P / {psutil.cpu_count(logical=True)}L\n"
            f"Freq: {cpufreq.current:.2f}Mhz\n"
            f"Load: {cpu_load}%\n"
            f"```\n"
            f"🧠 **MEMORY**\n"
            f"```\n"
            f"Total: {get_size(svmem.total)}\n"
            f"Used: {get_size(svmem.used)} ({svmem.percent}%)\n"
            f"Free: {get_size(svmem.available)}\n"
            f"```\n"
            f"💾 **DISK USAGE**\n"
            f"```\n"
            f"{disk_info.strip()}\n"
            f"```\n"
            f"🔝 **TOP PROCESSES (By Mem)**\n"
            f"```\n"
            f"{proc_info.strip()}\n"
            f"```"
        )
        
        try:
            await update.message.reply_markdown(report)
        except Exception as e:
            logger.error(f"Markdown failed, sending plain text: {e}")
            await update.message.reply_text(report.replace("*", "").replace("`", ""))
        logger.info(f"Sent detailed report to {user.first_name}")

    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        await update.message.reply_text(f"❌ Failed to generate report: {e}")
