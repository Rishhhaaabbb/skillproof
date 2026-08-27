// Task 10: Card displaying a single personalised skill-building task
import type { Task } from '@/lib/types';

interface TaskCardProps {
  task: Task;
  onComplete?: (taskId: number) => void;
}

export default function TaskCard({ task, onComplete }: TaskCardProps) {
  return (
    <div className="rounded-lg border p-4">
      <p className="font-medium">{task.task_description}</p>
      <span className={`text-xs ${task.status === 'verified_complete' ? 'text-green-600' : 'text-gray-500'}`}>
        {task.status}
      </span>
      {/* Full implementation in Task 10 */}
    </div>
  );
}
