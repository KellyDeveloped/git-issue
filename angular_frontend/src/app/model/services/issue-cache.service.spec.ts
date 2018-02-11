import { TestBed, inject } from '@angular/core/testing';

import { IssueCacheService } from './issue-cache.service';

describe('IssueCacheService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [IssueCacheService]
    });
  });

  it('should be created', inject([IssueCacheService], (service: IssueCacheService) => {
    expect(service).toBeTruthy();
  }));
});
