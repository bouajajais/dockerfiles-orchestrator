from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import sys
import time
from typing import Callable, Iterable, Optional, TypeVar

InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")
InputIndex = int
SkippedCounter = int
StartTime = float
Elapsed = float
ETA = float

def parallelize(
    func: Callable[[InputType, InputIndex, Iterable[InputType]], OutputType],
    data: Iterable[InputType],
    printer: Optional[Callable[[Iterable[InputType], InputType, InputIndex, SkippedCounter, StartTime, Elapsed, ETA], str]] = None,
    verbose: int = 1,
    n_jobs: int = 8
    ):
    """
    Parallelizes the execution of a function over a dataset using multithreading.

    Parameters
    ----------
        func : Callable[[InputType, InputIndex, Iterable[InputType]], OutputType]
            The function to be executed in parallel. It should accept three arguments: 
            a piece of data, the current index, and the entire dataset.
        data : Iterable[InputType]
            The dataset to be processed.
        printer : Callable[[Iterable[InputType], InputType, InputIndex, SkippedCounter, StartTime, Elapsed, ETA], str], optional
            A function that prints the progress of the parallelization process. 
            It should accept the dataset, the current piece of data, the current index, 
            the number of skipped pieces, the start time, the elapsed time, and the estimated time of arrival.
            The default is None.
        n_jobs : int, optional
            The number of threads to be used. The default is 8.
            
    Returns
    -------
        List[OutputType]
            The results of the function applied to each piece
    """
    if printer is None:
        printer = lambda data, piece, piece_index, skipped_counter, start_time, elapsed, eta: ""
    
    # Use a shared counter that can be incremented by each thread without race conditions
    piece_index = multiprocessing.Value('i', 0)
    skipped_counter = multiprocessing.Value('i', 0)
    start_time = time.time()
    
    def func_wrapper(piece: InputType) -> OutputType:
        nonlocal piece_index, skipped_counter, start_time
        
        elapsed = round(time.time() - start_time)
        
        current_index = None
        
        with piece_index.get_lock(), skipped_counter.get_lock():
            eta = (elapsed / (piece_index.value - skipped_counter.value + 1)) * (len(data) - piece_index.value)
            
            external_print = printer(data, piece, piece_index.value, skipped_counter.value, start_time, elapsed, eta)
            if external_print != "":
                external_print = f" ({external_print})"

            if verbose >= 1:
                sys.stdout.write("\033[K")
                print(f"Processing piece {piece_index.value + 1}/{len(data)} [skipped={skipped_counter.value}]{external_print}; time elapsed = {elapsed} seconds; ETA = {round(eta)} seconds.\r", end="")
            
            current_index = piece_index.value
            piece_index.value += 1
            
        result = func(piece, current_index, data)
        
        if isinstance(result, dict) and result.get("skipped", False):
            with skipped_counter.get_lock():
                skipped_counter.value += 1
                
        return result
    
    with ThreadPoolExecutor(max_workers=n_jobs) as executor:
        results = list(executor.map(func_wrapper, data))
    
    elapsed = round(time.time() - start_time)
            
    external_print = printer(data, None, None, skipped_counter.value, start_time, elapsed, None)
    if external_print != "":
        external_print = f" ({external_print})"
    
    if verbose >= 1:
        sys.stdout.write("\033[K")
    if verbose >= 2:
        print(f"Processed {len(data)} pieces [skipped={skipped_counter.value}]{external_print}; time elapsed = {elapsed} seconds")
    
    return results