
def intervals_intersection_length(pupil: tuple, tutor: tuple) -> int:
    '''
    count how much seconds pupil and tutor were online at same time 
    
    -------     pupil  = [a1,b1]
      -------   tutor    = [a2,b2]
      -----     common time = 5s
    '''
    a1, b1 = pupil
    a2, b2 = tutor

    if b1 < a2 or b2 < a1:
        return 0          # no intersection at all
    else:
        return min(b1, b2) - max(a1, a2) # min right - max left border <=> intersection length




def handle_overlapping_interval(prev: tuple[int], next: tuple[int]) -> tuple[int]:
    '''
    - see test #2 as refference of overlapping intervals 

     some intervals are overlapping each other - so check if
     a) next is completly witin prev 
        => 'a'
     b) next lasts longer than prev 
        => 'b'
     c) next has no overlapping with prev <=> new interval has started 
        => 'c'

    so as a result we have (not)extended previous interval or new interval '''
    
    if next[0] > prev[1]:
        # c) next has no overlapping with prev
        return next
    # a,b) check kind of overlapping
    if next[1] <= prev[1]:
        # a) complete overlapping
        return prev
    # b) next lasts longer than prev => return merged interval 
    return prev[0], next[1]





def appearance(intervals: dict[str, list[int]]) -> int:
       
    min_t, max_t = intervals['lesson'] # time when lesson goes - other intervals must be within this borders [min_t, max_t]  

    def handle_interval_fit(a: int, b: int) -> tuple[int] | bool:
        '''
        check if interval fits lesson`s interval: [min_t, max_t]
        move left or right border to edge value if it crosses it (min_t/max_t responsively for a and b)
        output: 
            tuple - tuple that fits lesson`s tuple-interval
            False - if [a,b] interval completly out of [min_t, max_t] interval
        ''' 
        # check if [a,b] has no intersection with [min_t, max_t]
        if a < min_t or a > max_t:
            return False
        
        # correct a or b to the border if it exeeds [min_t, max_t] interval
        if a < min_t:
            a = min_t
        if b > max_t: 
            b = max_t
        return a, b
    
    def get_a_b(interval_idx: int, content: str, prev: tuple[int] = None) -> tuple[tuple[int] | bool, bool]:
        '''
        Function used in crawler like payload function - handles everything related with intervals

        prev - previous UNITED interval

        get interval`s borders by given index
        and know if previous united interval was complete - by previous_ready flag
        
        - also check&fix if it doesn`t fits lesson`s interval
        '''
        i = interval_idx*2 # real index
        a, b = intervals[content][i], intervals[content][i+1] # take left and right borders: [a, b] for next inteval
        

        previous_ready = False # flag that tells if the previous interval was completed (non-overlaping old interval, that gathered and merged all subintervals inside)
        
        # if there`s previous interval => check and handle possible overlapping 
        if i> 0 and prev:
            a_, b_ = handle_overlapping_interval(prev, (a, b))
            # if new left border (_a) > old left border (prev[0]) => there is no new interval - was overlapping  
            if a_ > prev[0]:
                # if start of old and new intervals are different => we`ve got new interval and previous is ready
                previous_ready = True


        # return [a,b] interval`s part that fits lesson time or False
        return handle_interval_fit(a, b), previous_ready


    # if some of 3 intervals is empty => there`s no intersection at all
    if 0 in (len(x) for x in (intervals['lesson'], intervals['pupil'], intervals['tutor'])):
        return 0

    shared_time = 0 
    sec, prev_sec = 0, 0  # used to store value of intervals intersecton - for last and previous ones 
    last_flag = False # flag to indicate last loop
    # start and end indexes for pupil and tutor intervals
    pupil_i, tutor_i = 0, 0
    pupil_n, tutor_n = len(intervals['pupil'])//2 - 1, len(intervals['tutor'])//2 - 1

    pupil, previous_ready_p, tutor, previous_ready_t = *get_a_b(0, 'pupil'), *get_a_b(0, 'tutor') # init start intervals
    '''
    Main loop
        two pointers: pupil_i and tutor_i - for two corresponding intervals
        - each time move one of pointers to find intersection for next combination of intervals
    '''    
    
    while True:
        # get intervals by pointers (already cutten to fit in lesson`s scope)
        pupil, previous_ready_p = get_a_b(pupil_i, 'pupil', pupil)
        tutor, previous_ready_t = get_a_b(tutor_i, 'tutor', tutor)

        # Itterate until both intervals are in lesson`s scope (not False): increment pointers that aren`t fit lesson`s interval and reitterate(continue) until they fit (or until both indexes become edged) 
        if not (pupil and tutor):
            if not pupil and pupil_i < pupil_n:
                pupil_i += 1
            if not tutor and tutor_i < tutor_n:
                tutor_i += 1
            # go to next loop - to check if there`s intervals that fits in lesson time
            continue
        
        # check if remaining intervals are already exceeded 
        if pupil[0] > max_t and tutor[0] > max_t:
            return shared_time


        # ======= Bellow both intervals are within lesson`s time: =======

        # 1. fix(select) particular tutor`s interval
        # 2. move through tutor`s intervals until there`s no intersection with pupil`s
        # 3. if no intersection - repeat step 1. with next interval
        
        prev_sec = sec
        sec = intervals_intersection_length(pupil, tutor)

        # move pointers
        if sec > 0:     
            if pupil_i < pupil_n:   
                pupil_i += 1
            # if all pupil-intervals were already watched - try watch tutor`s 
            elif tutor_i < tutor_n:
                tutor_i += 1
        else:
            if tutor_i < tutor_n:
                tutor_i += 1
            # if all tutor`s-intervals were already watched - try watch pupils`s
            elif pupil_i < pupil_n:   
                pupil_i += 1
        
        # add length of previous interval (consissting of overlapping intervals inside it) when new interval was found
        if previous_ready_t or previous_ready_p:
            shared_time += prev_sec

        # check if we`ve watched last combination of intervals                
        if last_flag:
            shared_time += sec # due it`s last loop - add length of intersection for last interval
            return shared_time
        
        # check if we must watch last combination of intervals
        if pupil_i == pupil_n and tutor_i == tutor_n:
            last_flag = True


# time-intervals (in seconds) 159466 33 - 159466 68
# start1 --- end1 --- start2 --- end2 --- start3 --- end3 --- ... 
tests = [
    {'intervals': {'lesson': [1594663200, 1594666800],
             'pupil': [1594663340, 1594663389, 1594663390, 1594663395, 1594663396, 1594666472],
             'tutor': [1594663290, 1594663430, 1594663443, 1594666473]},
     'answer': 3117
    },
    {'intervals': {'lesson': [1594702800, 1594706400],
             'pupil': [1594702789, 1594704500, 1594702807, 1594704542, 1594704512, 1594704513, 1594704564, 1594705150, 1594704581, 1594704582, 1594704734, 1594705009, 1594705095, 1594705096, 1594705106, 1594706480, 1594705158, 1594705773, 1594705849, 1594706480, 1594706500, 1594706875, 1594706502, 1594706503, 1594706524, 1594706524, 1594706579, 1594706641],
             'tutor': [1594700035, 1594700364, 1594702749, 1594705148, 1594705149, 1594706463]},
    'answer': 3577
    },
    {'intervals': {'lesson': [1594692000, 1594695600],
             'pupil': [1594692033, 1594696347],
             'tutor': [1594692017, 1594692066, 1594692068, 1594696341]},
    'answer': 3565
    },
]

#tests = [tests[1]] # only 2nd test

if __name__ == '__main__':
   for i, test in enumerate(tests):
       test_answer = appearance(test['intervals'])
       assert test_answer == test['answer'], f'Error on test case {i}, got {test_answer}, expected {test["answer"]}'
