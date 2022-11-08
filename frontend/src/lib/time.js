import dayjs from 'dayjs';
import relativeTimePlugin from 'dayjs/plugin/relativeTime';
import durationPlugin from 'dayjs/plugin/duration';

dayjs.extend(relativeTimePlugin);
dayjs.extend(durationPlugin);


export default {
    seconds_to_string: function(time_num) {
        if (!time_num || time_num === 0) {
            return "";
        }
        const time_obj = dayjs(time_num*1000);
        return time_obj.fromNow();
    },
    seconds_duration: function(time_num1, time_num2) {
        const time_obj1 = dayjs(time_num1*1000);
        const time_obj2 = dayjs(time_num2*1000);
        var duration = dayjs.duration(time_obj2.diff(time_obj1));
        return duration.humanize();
    }
}
 