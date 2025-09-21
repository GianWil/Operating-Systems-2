from mmu import MMU

class LruMMU(MMU):
    def __init__(self, frames):
        # TODO: Constructor logic for LruMMU
        self.num_frames = int(frames)
        self.frames = [{'page': None, 'dirty': False, 'last_used': -1} for _ in range(self.num_frames)]
        self.page_to_frame = {}
        self.free = list(range(self.num_frames))[::-1]
        self._disk_reads = 0
        self._disk_writes = 0
        self._page_faults = 0
        self._time = 0
        self._debug = False

    def set_debug(self):
        # TODO: Implement the method to set debug mode
        self._debug = True
       

    def reset_debug(self):
        # TODO: Implement the method to reset debug mode
        self._debug = False
       

    def read_memory(self, page_number):
        # TODO: Implement the method to read memory
        self._access(page_number, False)
        

    def write_memory(self, page_number):
        # TODO: Implement the method to write memory
        self._access(page_number, True)
       

    def get_total_disk_reads(self):
        # TODO: Implement the method to get total disk reads
        return self._disk_reads
        

    def get_total_disk_writes(self):
        # TODO: Implement the method to get total disk writes
        return self._disk_writes

    def get_total_page_faults(self):
        # TODO: Implement the method to get total page faults
        return self._page_faults

    def _access(self, page, is_write):
        self._time += 1
        fidx = self.page_to_frame.get(page)
        if fidx is not None:
            fr = self.frames[fidx]
            fr['last_used'] = self._time
            if is_write:
                fr['dirty'] = True
            if self._debug:
                print(f"HIT {'W' if is_write else 'R'} page {page} in frame {fidx}")
            return
        self._page_faults += 1
        if self.free:
            fidx = self.free.pop()
            if self._debug:
                print(f"ALLOC frame {fidx} for page {page}")
        else:
            fidx = self._victim_lru_index()
            victim = self.frames[fidx]
            vpage, vdirty = victim['page'], victim['dirty']
            if vdirty:
                self._disk_writes += 1
                if self._debug:
                    print(f"EVICT DIRTY page {vpage} from frame {fidx}")
            else:
                if self._debug:
                    print(f"EVICT CLEAN page {vpage} from frame {fidx}")
            if vpage in self.page_to_frame:
                del self.page_to_frame[vpage]
        self._disk_reads += 1
        self.frames[fidx]['page'] = page
        self.frames[fidx]['dirty'] = bool(is_write)
        self.frames[fidx]['last_used'] = self._time
        self.page_to_frame[page] = fidx
        if self._debug:
            print(f"FAULT {'W' if is_write else 'R'} load page {page} into frame {fidx} (disk_read++)")

    def _victim_lru_index(self):
        min_idx = None
        min_time = None
        for i, fr in enumerate(self.frames):
            if fr['page'] is None:
                continue
            if min_time is None or fr['last_used'] < min_time:
                min_time = fr['last_used']
                min_idx = i
        return 0 if min_idx is None else min_idx