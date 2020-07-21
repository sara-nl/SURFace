# Configuration for slurm
Configuration data as of 2020-06-02T12:42:54

AllowSpecResourcesUsage = 0
  * If set to "YES", Slurm allows individual jobs to override node's configured CoreSpecCount value. For a job to take advantage of this feature, a command line option of --core-spec must be specified. The default value for this option is "YES" for Cray systems and "NO" for other system types.
    - 0 seems to indicate no or ignore

BatchStartTimeout       = 10 sec
  * The maximum time (in seconds) that a batch job is permitted for launching before being considered missing and releasing the allocation.

CompleteWait            = 0 sec
  * The time, in seconds, given for a job to remain in COMPLETING state before any additional jobs are scheduled. If set to zero, pending jobs will be started as soon as possible. Since a COMPLETING job's resources are released for use by other jobs as soon as the Epilog completes on each individual node, this can result in very fragmented resource allocations. To provide jobs with the minimum response time, a value of zero is recommended (no waiting). To minimize fragmentation of resources, a value equal to KillWait plus two is recommended. In that case, setting KillWait to a small value may be beneficial. The default value of CompleteWait is zero seconds. The value may not exceed 65533.

CpuFreqGovernors        = Performance,OnDemand,UserSpace
  * List of CPU frequency governors allowed to be set with the salloc, sbatch, or srun option --cpu-freq. Acceptable values at present include:
    - Performance: attempts to use the Performance CPU governor (a default value)
    - OnDemand: attempts to use the OnDemand CPU governor (a default value)
    - UserSpace: attempts to use the UserSpace CPU governor (a default value)

DefMemPerNode           = UNLIMITED
  * Default real memory size available per allocated node in megabytes. Used to avoid over-subscribing memory and causing paging. DefMemPerNode would generally be used if whole nodes are allocated to jobs (SelectType=select/linear) and resources are over-subscribed (OverSubscribe=yes or OverSubscribe=force). The default value is 0 (unlimited). Also see DefMemPerCPU, DefMemPerGPU and MaxMemPerCPU. DefMemPerCPU, DefMemPerGPU and DefMemPerNode are mutually exclusive.

EioTimeout              = 60
  * The number of seconds srun waits for slurmstepd to close the TCP/IP connection used to relay data between the user application and srun when the user application terminates. The default value is 60 seconds. May not exceed 65533.

EnforcePartLimits       = ALL
  * If set to "ALL" then jobs which exceed a partition's size and/or time limits will be rejected at submission time. If job is submitted to multiple partitions, the job must satisfy the limits on all the requested partitions.

EpilogMsgTime           = 2000 usec
  * The number of microseconds that the slurmctld daemon requires to process an epilog completion message from the slurmd daemons.
      This parameter can be used to prevent a burst of epilog completion messages from being sent at the same time which should help
      prevent lost messages and improve throughput for large jobs.

FairShareDampeningFactor = 1
  * Dampen the effect of exceeding a user or group's fair share of allocated resources. Higher values will provides greater ability to differentiate between exceeding the fair share at high levels (e.g. a value of 1 results in almost no difference between overconsumption by a factor of 10 and 100, while a value of 5 will result in a significant difference in priority). The default value is 1.

FastSchedule            = 1
  *  1 is the default value

GetEnvTimeout           = 2 sec
  * Controls how long the job should wait (in seconds) to load the user's environment before attempting to load it from a cache file.
      Applies when the salloc or sbatch --get-user-env option is used. If set to 0 then always load the user's environment from the cache file.
      The default value is 2 seconds.

GpuFreqDef              = high,memory=high
  * Default GPU frequency to use when running a job step if it has not been explicitly set using the --gpu-freq option. This option can be used to independently configure the GPU and its memory frequencies. Defaults to "high,memory=high"
    - high: the highest available frequency.

KeepAliveTime           = SYSTEM_DEFAULT
  * Specifies how long sockets communications used between the srun command and its slurmstepd process are kept alive after disconnect. Longer values can be used to improve reliability of communications in the event of network failures. The default value leaves the system default value.

KillOnBadExit           = 0
  * If set to 1, a step will be terminated immediately if any task is crashed or aborted, as indicated by a non-zero exit code. With the default value of 0, if one of the processes is crashed or aborted the other processes will continue to run while the crashed or aborted process waits. The user can override this configuration parameter by using srun's -K, --kill-on-bad-exit.

KillWait                = 30 sec
  * The interval, in seconds, given to a job's processes between the SIGTERM and SIGKILL signals upon reaching its time limit. If the job fails to terminate gracefully in the interval specified, it will be forcibly terminated.

LogTimeFormat           = iso8601_ms
  * Format of the timestamp in slurmctld and slurmd log files.

MaxArraySize            = 1001
  * The maximum job array size. The maximum job array task index value will be one less than MaxArraySize to allow for an index value of zero.
    - this means largest array job possible is of size 1000

MaxJobCount             = 100000
  * The maximum number of jobs Slurm can have in its active database at one time. Set the values of MaxJobCount and MinJobAge to ensure the slurmctld daemon does not exhaust its memory or other resources. Once this limit is reached, requests to submit additional jobs will fail. The default value is 10000 jobs.
    - note jobarrays count as one job

MaxMemPerNode           = UNLIMITED
  * Maximum real memory size available per allocated node in megabytes. Used to avoid over-subscribing memory and causing paging. MaxMemPerNode would generally be used if whole nodes are allocated to jobs.

MaxStepCount            = 40000
  * The maximum number of steps that any job can initiate. This parameter is intended to limit the effect of bad batch scripts. The default value is 40000 steps.

MaxTasksPerNode         = 512
  * Maximum number of tasks Slurm will allow a job step to spawn on a single node. The default MaxTasksPerNode is 512. May not exceed 65533.

MessageTimeout          = 45 sec
  * Time permitted for a round-trip communication to complete in seconds. Default value is 10 seconds. For systems with shared nodes, the slurmd daemon could be paged out and necessitate higher values.

OverTimeLimit           = 0 min
  * Number of minutes by which a job can exceed its time limit before being canceled.

PowerParameters         = (null)
  * System power management parameters.
    - unused

PowerPlugin             =
  * unset

PreemptMode             = OFF
  * Mechanism used to preempt jobs or enable gang scheudling.
    - disabled

PriorityFlags           = MAX_TRES
  * Flags to modify priority behavior. Applicable only if PriorityType=priority/multifactor.
    - MAX_TRES: If set, the weighted TRES value (e.g. TRESBillingWeights) is calculated as the MAX of individual TRES' on a node (e.g. cpus, mem, gres) plus the sum of all global TRES' (e.g. licenses).

PriorityMaxAge          = 7-00:00:00
  * Specifies the job age which will be given the maximum age factor in computing priority. For example, a value of 30 minutes would result in all jobs over 30 minutes old would get the same age-based priority.
    - Applicable only if PriorityType=priority/multifactor. The unit is a time string (i.e. min, hr:min:00, days-hr:min:00, or days-hr).

PriorityUsageResetPeriod = NONE
  * At this interval the usage of associations will be reset to 0. This is used if you want to enforce hard limits of time usage per association.

PriorityType            = priority/multifactor
  * This specifies the plugin to be used in establishing a job's scheduling priority. Supported values are "priority/basic" (jobs are prioritized by order of arrival), "priority/multifactor" (jobs are prioritized based upon size, age, fair-share of allocation, etc).

PriorityWeightAge       = 100000
  * An integer value that sets the degree to which the queue wait time component contributes to the job's priority. Applicable only if PriorityType=priority/multifactor.

PriorityWeightAssoc     = 0
  * An integer value that sets the degree to which the association component contributes to the job's priority.

PriorityWeightFairShare = 1000000
  * An integer value that sets the degree to which the fair-share component contributes to the job's priority.

PriorityWeightJobSize   = 0
  * An integer value that sets the degree to which the job size component contributes to the job's priority.

PriorityWeightPartition = 1000000
  * Partition factor used by priority/multifactor plugin in calculating job priority.

PriorityWeightQOS       = 0
  * An integer value that sets the degree to which the Quality Of Service component contributes to the job's priority.

PriorityWeightTRES      = (null)
  * A comma separated list of TRES Types and weights that sets the degree that each TRES Type contributes to the job's priority.
    - e.g. PriorityWeightTRES=CPU=1000,Mem=2000,GRES/gpu=3000

ProctrackType           = proctrack/cgroup
  * Identifies the plugin to be used for process tracking on a job step basis. The slurmd daemon uses this mechanism to identify all processes which are children of processes it spawns for a user job step.
    - proctrack/cgroup: which uses linux cgroups to constrain and track processes, and is the default. NOTE: see "man cgroup.conf" for configuration details

PrologEpilogTimeout     = 3600
  * The interval in seconds Slurms waits for Prolog and Epilog before terminating them.

PrologFlags             = Alloc,Contain,X11
  * Flags to control the Prolog behavior. By default no flags are set. Multiple flags may be specified in a comma-separated list.
    - Alloc: If set, the Prolog script will be executed at job allocation. By default, Prolog is executed just before the task is launched. Therefore, when salloc is started, no Prolog is executed. Alloc is useful for preparing things before a user starts to use any allocated resources. In particular, this flag is needed on a Cray system when cluster compatibility mode is enabled. NOTE: Use of the Alloc flag will increase the time required to start jobs.
    - Contain: At job allocation time, use the ProcTrack plugin to create a job container on all allocated compute nodes. This container may be used for user processes not launched under Slurm control.
    - X11: Enable Slurm's built-in X11 forwarding capabilities.

PropagatePrioProcess    = 0
  * Controls the scheduling priority (nice value) of user spawned tasks.
    - 0: The tasks will inherit the scheduling priority from the slurm daemon.

PropagateResourceLimits = ALL
  * A list of comma separated resource limit names. The slurmd daemon uses these names to obtain the associated (soft) limit values from the user's process environment on the submit node.
  * ALL: All limits listed below (default)
    - AS: The maximum address space for a process
    - CORE: The maximum size of core file
    - CPU: The maximum amount of CPU time
    - DATA: The maximum size of a process's data segment
    - FSIZE: The maximum size of files created. Note that if the user sets FSIZE to less than the current size of the slurmd.log, job launches will fail with a 'File size limit exceeded' error.
    - MEMLOCK: The maximum size that may be locked into memory
    - NOFILE: The maximum number of open files
    - NPROC: The maximum number of processes available
    - RSS: The maximum resident set size
    - STACK:The maximum stack size
  * Documentation doesn't list default values for these.

PropagateResourceLimitsExcept = (null)
  * A list of comma separated resource limit names.
    - null

RequeueExit             = (null)
  * Enables automatic requeue for batch jobs which exit with the specified values.

RequeueExitHold         = (null)
  * Enables automatic requeue for batch jobs which exit with the specified values, with these jobs being held until released manually by the user.

ResumeProgram           = (null)
  * Slurm supports a mechanism to reduce power consumption on nodes that remain idle for an extended period of time. This is typically accomplished by reducing voltage and frequency or powering the node down. ResumeProgram is the program that will be executed when a node in power save mode is assigned work to perform.

ResumeRate              = 300 nodes/min
  * The rate at which nodes in power save mode are returned to normal operation by ResumeProgram.

ResumeTimeout           = 600 sec
  * Maximum time permitted (in seconds) between when a node resume request is issued and when the node is actually available for use.

ResvOverRun             = 0 min
  * Describes how long a job already running in a reservation should be permitted to execute after the end time of the reservation has been reached.
    - 0 = kill the job immediately

ReturnToService         = 1
  * Controls when a DOWN node will be returned to service.
    - 1 = A DOWN node will become available for use upon registration with a valid configuration only if it was set DOWN due to being non-responsive. If the node was set DOWN for any other reason (low memory, unexpected reboot, etc.), its state will not automatically be changed. A node registers with a valid configuration if its memory, GRES, CPU count, etc. are equal to or greater than the values configured in slurm.conf.

RoutePlugin             = route/default
  * Identifies the plugin to be used for defining which nodes will be used for message forwarding and message aggregation.
    - route/default: default, use TreeWidth

SchedulerParameters     = nohold_on_prolog_fail,max_switch_wait=7200,bf_max_job_start=10,sched_max_job_start=20,bf_continue,bf_interval=60,bf_max_job_test=500,bf_max_job_user=10,bf_resolution=300,bf_window=1440,kill_invalid_depend,max_rpc_cnt=150,
  * The interpretation of this parameter varies by SchedulerType.
    - nohold_on_prolog_fail: By default, if the Prolog exits with a non-zero value the job is requeued in a held state. By specifying this parameter the job will be requeued but not held so that the scheduler can dispatch it to another host.
    - max_switch_wait=#: Maximum number of seconds that a job can delay execution waiting for the specified desired switch count. The default value is 300 seconds.
    - bf_max_job_start=#: The maximum number of jobs which can be initiated in a single iteration of the backfill scheduler. This option applies only to SchedulerType=sched/backfill. Default: 0 (no limit), Min: 0, Max: 10000.
    - sched_max_job_start=#: The maximum number of jobs that the main scheduling logic will start in any single execution. The default value is zero, which imposes no limit.
    - bf_continue: The backfill scheduler periodically releases locks in order to permit other operations to proceed rather than blocking all activity for what could be an extended period of time. Setting this option will cause the backfill scheduler to continue processing pending jobs from its original job list after releasing locks even if job or node state changes.
    - bf_interval=#: The number of seconds between backfill iterations. Higher values result in less overhead and better responsiveness. This option applies only to SchedulerType=sched/backfill. Default: 30, Min: 1, Max: 10800 (3h).
    - bf_max_job_test=#: The maximum number of jobs to attempt backfill scheduling for (i.e. the queue depth). Higher values result in more overhead and less responsiveness. Until an attempt is made to backfill schedule a job, its expected initiation time value will not be set. In the case of large clusters, configuring a relatively small value may be desirable. This option applies only to SchedulerType=sched/backfill. Default: 100, Min: 1, Max: 1,000,000.
    - bf_max_job_user=#: The maximum number of jobs per user to attempt starting with the backfill scheduler for ALL partitions. One can set this limit to prevent users from flooding the backfill queue with jobs that cannot start and that prevent jobs from other users to start. This is similar to the MAXIJOB limit in Maui. This option applies only to SchedulerType=sched/backfill. Also see the bf_max_job_part, bf_max_job_test and bf_max_job_user_part=# options. Set bf_max_job_test to a value much higher than bf_max_job_user. Default: 0 (no limit), Min: 0, Max: bf_max_job_test.
    - bf_resolution=#: The number of seconds in the resolution of data maintained about when jobs begin and end. Higher values result in less overhead and better responsiveness. This option applies only to SchedulerType=sched/backfill. Default: 60, Min: 1, Max: 3600 (1 hour).
    - bf_window=#: The number of minutes into the future to look when considering jobs to schedule. Higher values result in more overhead and less responsiveness. A value at least as long as the highest allowed time limit is generally advisable to prevent job starvation. In order to limit the amount of data managed by the backfill scheduler, if the value of bf_window is increased, then it is generally advisable to also increase bf_resolution. This option applies only to SchedulerType=sched/backfill. Default: 1440 (1 day), Min: 1, Max: 43200 (30 days).
    - kill_invalid_depend: If a job has an invalid dependency and it can never run terminate it and set its state to be JOB_CANCELLED.
    - max_rpc_cnt=#: If the number of active threads in the slurmctld daemon is equal to or larger than this value, defer scheduling of jobs. The scheduler will check this condition at certain points in code and yield locks if necessary. This can improve Slurm's ability to process requests at a cost of initiating new jobs less frequently. Default: 0 (option disabled), Min: 0, Max: 1000.
      - NOTE: The maximum number of threads (MAX_SERVER_THREADS) is internally set to 256 and defines the number of served RPCs at a given time. Setting max_rpc_cnt to more than 256 will be only useful to let backfill continue scheduling work after locks have been yielded (i.e. each 2 seconds) if there are a maximum of MAX(max_rpc_cnt/10, 20) RPCs in the queue. i.e. max_rpc_cnt=1000, the scheduler will be allowed to continue after yielding locks only when there are less than or equal to 100 pending RPCs. If a value is set, then a value of 10 or higher is recommended. It may require some tuning for each system, but needs to be high enough that scheduling isn't always disabled, and low enough that requests can get through in a reasonable period of time.

SchedulerTimeSlice      = 30 sec
  * Number of seconds in each time slice when gang scheduling is enabled (PreemptMode=SUSPEND,GANG). default is 30s

SchedulerType           = sched/backfill
  * Identifies the type of scheduler to be used.
    - sched/backfill: For a backfill scheduling module to augment the default FIFO scheduling. Backfill scheduling will initiate lower-priority jobs if doing so does not delay the expected initiation time of any higher priority job. Effectiveness of backfill scheduling is dependent upon users specifying job time limits, otherwise all jobs will have the same time limit and backfilling is impossible. Note documentation for the SchedulerParameters option above. This is the default configuration.

SelectType              = select/cons_tres
  * Identifies the type of resource selection algorithm to be used.
    - select/cons_tres: The resources (cores and memory) within a node are individually allocated as consumable resources. Note that whole nodes can be allocated to jobs for selected partitions by using the OverSubscribe=Exclusive option. See the partition OverSubscribe parameter for more information.

SelectTypeParameters    = CR_CORE_MEMORY
  * The permitted values of SelectTypeParameters depend upon the configured value of SelectType.
    - CR_CORE_MEMORY: Cores and memory are consumable resources. On nodes with hyper-threads, each thread is counted as a CPU to satisfy a job's resource requirement, but multiple jobs are not allocated threads on the same core. The count of CPUs allocated to a job may be rounded up to account for every CPU on an allocated core. Setting a value for DefMemPerCPU is strongly recommended.

SlurmdTimeout           = 300 sec
  * The interval, in seconds, that the Slurm controller waits for slurmd to respond before configuring that node's state to DOWN.

SLURM_VERSION           = 19.05.3-2
  * version
{
  Seems suspend may be disabled
  SuspendExcNodes         = (null)
    * Specifies the nodes which are to not be placed in power save mode, even if the node remains idle for an extended period of time.
  SuspendExcParts         = (null)
    * Specifies the partitions whose nodes are to not be placed in power save mode
  SuspendProgram          = (null)
    * SuspendProgram is the program that will be executed when a node remains idle for an extended period of time. This program is expected to place the node into some power save mode.
  SuspendRate             = 60 nodes/min
    * The rate at which nodes are placed into power save mode by SuspendProgram. The value is number of nodes per minute and it can be used to prevent a large drop in power consumption
  SuspendTime             = NONE
    * Nodes which remain idle or down for this number of seconds will be placed into power save mode by SuspendProgram.
  SuspendTimeout          = 30 sec
    * Maximum time permitted (in seconds) between when a node suspend request is issued and when the node is shutdown. At that time the node must be ready for a resume request to be issued as needed for new work
}

TaskPlugin              = task/cgroup
  * Identifies the type of task launch plugin, typically used to provide resource management within a node (e.g. pinning tasks to specific processors).
    - task/cgroup: enables resource containment using Linux control cgroups. This enables the --cpu-bind and/or --mem-bind srun options. NOTE: see "man cgroup.conf" for configuration details.

TCPTimeout              = 2 sec
  * Time permitted for TCP connection to be established. Default value is 2 seconds.

TopologyPlugin          = topology/tree
  * Identifies the plugin to be used for determining the network topology and optimizing job allocations to minimize network contention.
    - topology/tree: used for a hierarchical network as described in a topology.conf file

TreeWidth               = 50
  * Slurmd daemons use a virtual tree network for communications. TreeWidth specifies the width of the tree (i.e. the fanout). On architectures with a front end node running the slurmd daemon, the value must always be equal to or greater than the number of front end nodes which eliminates the need for message forwarding between the slurmd daemons.

UsePam                  = 0
  * PAM is used to establish the upper bounds for resource limits. 0 = disabled

VSizeFactor             = 0 percent
  * Memory specifications in job requests apply to real memory size (also known as resident set size). It is possible to enforce virtual memory limits for both jobs and job steps by limiting their virtual memory to some percentage of their real memory allocation.

WaitTime                = 0 sec
  * Specifies how many seconds the srun command should by default wait after the first task terminates before terminating all remaining tasks.


## Cgroup Support Configuration:
AllowedKmemSpace        = (null)
  * Constrain the job cgroup kernel memory to this  amount  of  the  allocated  memory, specified in bytes.

AllowedRAMSpace         = 100.0%
  * Constrain the job cgroup RAM to this  percentage  of  the  allocated  memory.

AllowedSwapSpace        = 0.0%
  * Constrain the job cgroup swap space to this percentage  of  the  allocated  memory.

CgroupAutomount         = yes
  * Slurm  cgroup  plugins  require valid and functional cgroup subsystem to be mounted
              under  /sys/fs/cgroup/<subsystem_name>.   When  launched,   plugins   check   their
              subsystem   availability.   If  not  available,  the  plugin  launch  fails  unless
              CgroupAutomount is set to yes. In that case, the plugin will first try to mount the
              required subsystems.

ConstrainCores          = yes
  *  If configured to "yes" then constrain allowed cores  to  the  subset  of  allocated
              resources.  This  functionality  makes  use  of the cpuset subsystem.  Due to a bug
              fixed in version 1.11.5 of HWLOC, the  task/affinity  plugin  may  be  required  in
              addition to task/cgroup for this to function properly.  The default value is "no".

ConstrainDevices        = yes
  *  If  configured  to  "yes"  then  constrain  the job's allowed devices based on GRES
              allocated resources. It uses the devices subsystem for that.  The default value  is
              "no".

ConstrainKmemSpace      = no
  * If  configured to "yes" then constrain the job's Kmem RAM usage. In addition to RAM
              usage. Only takes effect if ConstrainRAMSpace is set to "yes". The default value is
              "yes",  in  which case the job's Kmem limit will be set to its RAM limit.  Also see
              AllowedKmemSpace.

ConstrainRAMSpace       = yes
  * If configured to "yes" then constrain the job's RAM usage  by  setting  the  memory
              soft  limit  to  the  allocated memory and the hard limit to the allocated memory *
              AllowedRAMSpace.

ConstrainSwapSpace      = yes
  * If  configured  to  "yes"  then  constrain the job's swap space usage.  The default
              value is "no".

MaxKmemPercent          = 100.0%
  * Set  an  upper bound in percent of total RAM on the RAM constraint for a job.

MaxRAMPercent           = 100.0%
  *  Set  an  upper bound in percent of total RAM on the RAM constraint for a job.  This
              will be the memory constraint applied to jobs that  are  not  explicitly  allocated
              memory  by  Slurm  (i.e.  Slurm's  select plugin is not configured to manage memory
              allocations).

MaxSwapPercent          = 100.0%
  * Set  an upper bound (in percent of total RAM) on the amount of RAM+Swap that may be
              used for a job.

MemorySwappiness        = (null)
  * Configure  the  kernel's priority for swapping out anonymous pages (such as program
              data) verses file cache pages for the job cgroup

MinKmemSpace            = 30 MB
  * Set  a  lower  bound  (in MB) on the memory limits defined by AllowedKmemSpace. The
              default limit is 30M.

MinRAMSpace             = 30 MB
  *  Set a lower bound (in MB) on the  memory  limits  defined  by  AllowedRAMSpace  and
              AllowedSwapSpace.  This  prevents accidentally creating a memory cgroup with such a
              low limit that slurmstepd is immediately killed due to lack  of  RAM.

TaskAffinity            = yes
  * If configured to "yes" then set a default task affinity to bind each step task to a
              subset of the allocated cores using sched_setaffinity.
